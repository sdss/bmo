#!/usr/bin/env python
# encoding: utf-8
#
# manta.py
#
# Created by José Sánchez-Gallego on 7 Jan 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import gzip
import os
import time
import warnings

from twisted.internet import task

from distutils.version import StrictVersion

import astropy
import astropy.time
import astropy.io.fits as fits
import astropy.wcs as wcs

import numpy as np

from bmo.exceptions import BMOUserWarning, BMOMissingImportWarning, MantaError
from bmo.logger import log
from bmo.utils import PIXEL_SIZE, FOCAL_SCALE

try:
    from photutils import Background2D, SigmaClip, MedianBackground
    sigma_clip = SigmaClip(sigma=3., iters=3)
    bkg_estimator = MedianBackground()
except ImportError:
    warnings.warn('photutils is missing. Background subtraction will not work.',
                  BMOMissingImportWarning)
    Background2D = None


# These parameters can be overridden by the actor configuration.
UPDATE_INTERVAL = 3          # How frequently the available cameras will be checked.
EXTRA_EXPOSURE_DELAY = 1000  # How much extra time to wait for waitFrameCapture (ms).


def get_list_devices(config):
    """Returns a dictionary of ``'on'`` and ``'off'`` device ids."""

    on_axis = [dev.strip() for dev in config['cameras']['on_axis_devices'].split(',')]
    off_axis = [dev.strip() for dev in config['cameras']['off_axis_devices'].split(',')]

    return {'on': on_axis, 'off': off_axis}


def get_camera_position(device, config):
    """Returns the position ``'on_axis'`` or ``'off_axis'`` of ``device``.

    Returns ``None`` if the device is not found in the list of valid devices.

    """

    devices = get_list_devices(config)

    if device in devices['on']:
        return 'on'
    elif device in devices['off']:
        return 'off'
    else:
        return None


class MantaExposure(object):
    """A Manta camera exposure."""

    def __init__(self, data, exposure_time, camera_id,
                 camera_ra=None, camera_dec=None, extra_headers=[]):

        self.data = data
        self.exposure_time = np.round(exposure_time, 3)
        self.camera_id = camera_id
        self.obstime = astropy.time.Time.now().isot

        self.camera_ra = camera_ra
        self.camera_dec = camera_dec

        self.header = fits.Header([('EXPTIME', self.exposure_time),
                                   ('DEVICE', self.camera_id),
                                   ('OBSTIME', self.obstime)] + extra_headers)

    def subtract_background(self):
        """Fits a 2D background."""

        if Background2D is None:
            warnings.warn('photutils has not been installed.', BMOUserWarning)
            return

        bkg = Background2D(self.data, (50, 50), filter_size=(3, 3),
                           sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)

        self.data = self.data.astype(np.float64) - bkg.background

        return bkg

    def get_wcs_header(self, shape):
        """Returns an WCS header for an image of a certain ``shape``.

        It assumes the centre of the image corresponds to ``camera_ra, camera_dec``.

        """

        ww = wcs.WCS(naxis=2)
        ww.wcs.crpix = [shape[1] / 2., shape[0] / 2]
        ww.wcs.cdelt = np.array([FOCAL_SCALE * PIXEL_SIZE, FOCAL_SCALE * PIXEL_SIZE])
        ww.wcs.crval = [self.camera_ra, self.camera_dec]
        ww.wcs.ctype = ['RA---TAN', 'DEC--TAN']

        return ww.to_header()

    def save(self, basename=None, dirname='/data/acq_cameras', overwrite=False,
             compress=True, camera_ra=None, camera_dec=None, extra_headers=[]):

        header = self.header + fits.Header(extra_headers)

        if basename is None:
            timestr = time.strftime('%d%m%y_%H%M%S')
            basename = '{0}_{1}.fits'.format(self.camera_id, timestr)

        fn = os.path.join(dirname, basename)

        primary = fits.PrimaryHDU(data=self.data, header=header)

        self.camera_ra = camera_ra or self.camera_ra
        self.camera_dec = camera_dec or self.camera_dec

        # Not the nicest way of doing this but it seems to be the safest one.
        if self.camera_ra is not None and self.camera_dec is not None:

            primary.header['RACAM'] = self.camera_ra
            primary.header['DECCAM'] = self.camera_dec

            try:
                wcs_header = self.get_wcs_header(self.data.shape)
                for key in wcs_header:
                    primary.header[key] = wcs_header[key]
            except:
                warnings.warn('failed to create WCS header', BMOUserWarning)

        hdulist = fits.HDUList([primary])

        if overwrite is False:
            assert not os.path.exists(fn), \
                'the path exists. If you want to overwrite it use overwrite=True.'

        if compress:
            fn += '.gz'
            fobj = gzip.open(fn, 'wb')
        else:
            fobj = fn

        # Depending on the version of astropy, uses clobber or overwrite
        if StrictVersion(astropy.__version__) < StrictVersion('1.3.0'):
            hdulist.writeto(fobj, clobber=overwrite)
        else:
            hdulist.writeto(fobj, overwrite=overwrite)

        return fn

    @classmethod
    def from_fits(cls, fn):

        hdulist = fits.open(fn)
        new_object = MantaCamera.__new__(cls)

        new_object.data = hdulist[0].data
        new_object.header = hdulist[0].header
        new_object.camera_id = hdulist[0].header['DEVICE']
        new_object.exposure_time = float(hdulist[0].header['EXPTIME'])
        new_object.obstime = hdulist[0].header['OBSTIME']

        return new_object


class MantaCameraSet(object):

    def __init__(self, vimba, actor=None):

        self.actor = actor

        self.vimba = vimba
        log.debug('starting MantaCameraSet with vimba={!r}'.format(vimba))

        self.system = None

        self._init_controller()

        self.cameras = []
        self.connect_all()

        self.loop = None
        self._start_loop()

    def _init_controller(self):
        """Initialises the camera controller."""

        self.vimba.startup()

        self.system = self.vimba.getSystem()

        if self.system.GeVTLIsPresent:
            self.system.runFeatureCommand('GeVDiscoveryAllAuto')
            time.sleep(0.2)

        log.debug('Vimba system started.')

    def _start_loop(self):

        self.loop = task.LoopingCall(self._camera_check)

        # Overrides UPDATE_INTERVAL from the config file, if possible.
        if self.actor and 'update_interval' in self.actor.config['cameras']:
            self.loop.start(self.actor.config['cameras']['update_interval'])
        else:
            warnings.warn('cannot find update_interval in actor config. '
                          'Using default value for update camera interval.', BMOUserWarning)
            self.loop.start(UPDATE_INTERVAL)

    def _camera_check(self):
        """Checks connected cammeras and makes sure they are alive."""

        for camera_id in self.list_cameras():
            if camera_id not in self.get_camera_ids():
                if self.actor:
                    self.actor.writeToUsers('i', 'text="found camera {0}. '
                                                 'Connecting it."'.format(camera_id))
                log.info('found camera {0}.'.format(camera_id))
                self.connect(camera_id)
                return

        for camera_id in self.get_camera_ids():
            if camera_id not in self.list_cameras():
                self.disconnect(camera_id)
                return

    def connect(self, camera_id):
        """Connects a camera."""

        if camera_id not in self.list_cameras():
            raise ValueError('camera {0} is not connected'.format(camera_id))

        camera = MantaCamera(camera_id, self.vimba, self.system, actor=self.actor)

        self.cameras.append(camera)

    def connect_all(self, reconnect=True):
        """Connects all the available cameras."""

        if reconnect:
            for camera in self.cameras:
                self.disconnect(camera.camera_id)
            self.cameras = []

        for camera_id in self.list_cameras():
            self.connect(camera_id)

    def disconnect(self, camera_id):
        """Closes a camera and removes it from the list."""

        for camera in self.cameras:
            if camera_id == camera.camera_id:
                camera.close()
                self.cameras.remove(camera)

    def get_camera_ids(self):
        """Returns a list of connected camera ids."""

        return [camera.camera_id for camera in self.cameras]

    def list_cameras(self):

        cameras = self.vimba.getCameraIds()
        return cameras


class MantaCamera(object):

    def __init__(self, camera_id, vimba, system, actor=None):

        log.info('connecting camera {!r}'.format(camera_id))

        self.actor = actor

        self.vimba = vimba
        self.system = system

        self.is_busy = False
        self._exposure_cb = None  # The function that will be call when and exposure is done.

        self._camera_type = None

        self._last_exposure = None

        self.init_camera(camera_id)

    def init_camera(self, camera_id):

        if camera_id not in self.vimba.getCameraIds():
            raise ValueError('camera_id {0} not found. Cameras found: {1}'
                             .format(camera_id, self.cameras))

        self.camera = self.vimba.getCamera(camera_id)

        self.camera.openCamera()
        log.debug('camera open.')

        self.set_default_config()
        log.debug('default configuration set.')

        self.open = True
        self.camera_id = camera_id

        self.frame = self.camera.getFrame()
        log.debug('got new frame.')

        self.frame.announceFrame()
        log.debug('announced frame.')

        self.frame.queueFrameCapture(self.frame_callback)
        log.debug('queued frame.')

        self.camera.startCapture()
        log.debug('starting camera capture.')

        if self.actor:
            self.actor.writeToUsers('w', 'text="connected {0}"'.format(camera_id))
            if self.camera_type is not None:
                self.actor.cameras[self.camera_type] = self
            if 'extra_exposure_delay' in self.actor.config['cameras']:
                self._extra_exposure_delay = self.actor.config['cameras']['extra_exposure_delay']
            else:
                self._extra_exposure_delay = EXTRA_EXPOSURE_DELAY

    def set_default_config(self):

        self.camera.PixelFormat = 'Mono12'
        self.camera.ExposureTimeAbs = 1e6
        self.camera.AcquisionMode = 'SingleFrame'
        self.camera.GVSPPacketSize = 1500
        self.camera.GevSCPSPacketSize = 1500

    def expose(self, call_back_func=None):

        if self.is_busy:
            raise MantaError('camera is busy. Cannot expose now.')

        self._exposure_cb = call_back_func

        log.debug('starting exposure.')

        self.camera.runFeatureCommand('AcquisitionStart')
        self.camera.runFeatureCommand('AcquisitionStop')

    def frame_callback(self, frame):
        """Gets caled when the frame is filled."""

        log.debug('frame callback called. Processing image.')

        img_buffer = frame.getBufferByteData()
        img_data_array = np.ndarray(buffer=img_buffer,
                                    dtype=np.uint16,
                                    shape=(frame.height, frame.width))

        self._last_exposure = MantaExposure(img_data_array,
                                            self.camera.ExposureTimeAbs / 1e6,
                                            self.camera.cameraIdString)

        self.frame.queueFrameCapture(self.frame_callback)
        log.debug('requeued frame.')

        self.is_busy = False

        if self._exposure_cb is not None:
            log.debug('calling exposure callback function.')
            self._exposure_cb(self._last_exposure)

        return

    def save(self, fn, exposure=None, **kwargs):

        assert exposure is not None or self._last_exposure is not None, \
            'no exposure provided. Take an exposure before calling save.'

        exposure = exposure or self._last_exposure
        exposure.save(fn, **kwargs)

    def reconnect(self):
        """Closes and reconnects the camera."""

        self.close()
        self.init_camera(self.camera_id)

    @property
    def camera_type(self):
        """Returns ``'on'`` or ``'off'`` depending on the type of camera."""

        if self._camera_type is None:
            if self.actor is None:
                warnings.warn('cannot determine camera type', BMOUserWarning)

            camera_type = get_camera_position(self.camera_id, self.actor.config)

            if camera_type is None:
                warnings.warn('cannot determine camera type for {0}'.format(self.camera_id),
                              BMOUserWarning)

            self._camera_type = camera_type

        return self._camera_type

    def close(self):
        """Ends capture and closes the camera."""

        try:
            self.camera.endCapture()
            self.camera.revokeAllFrames()
            self.camera.closeCamera()
            # self.vimba.shutdown()
        except self.controller.VimbaException as ee:
            warnings.warn('failed closing the camera. Error: {0}'.format(str(ee)), BMOUserWarning)

        if self.actor:
            self.actor.writeToUsers('w', 'text="disconnected {0}"'.format(self.camera_id))
            if self.camera_type is not None:
                if self.actor.cameras[self.camera_type] is self:
                    self.actor.cameras[self.camera_type] = None

        self.open = False

    def __del__(self):
        """Destructor."""

        if self.open:
            self.close()
