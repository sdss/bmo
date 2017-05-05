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

from bmo.exceptions import BMOUserWarning, BMOError
from bmo.utils import PIXEL_SIZE, FOCAL_SCALE

try:

    import pymba

    vimba = pymba.Vimba()
    vimba.startup()

    system = vimba.getSystem()

    if system.GeVTLIsPresent:
        system.runFeatureCommand('GeVDiscoveryAllAuto')
        time.sleep(0.2)

except OSError:

    vimba = None


CAMERA_CHECK_LOOP_TIME = 3


def get_list_devices(config):
    """Returns a dictionary of ``'on'`` and ``'off'`` device ids."""

    on_axis = [dev.strip() for dev in config.get('cameras', 'on_axis_devices').split(',')]
    off_axis = [dev.strip() for dev in config.get('cameras', 'off_axis_devices').split(',')]

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

    def __init__(self, data, exposure_time, camera_id,
                 camera_ra=None, camera_dec=None,
                 extra_headers=[]):

        self.data = data
        self.exposure_time = np.round(exposure_time, 3)
        self.camera_id = camera_id
        self.obstime = astropy.time.Time.now().isot

        self.camera_ra = camera_ra
        self.camera_dec = camera_dec

        self.header = fits.Header([('EXPTIME', self.exposure_time),
                                   ('DEVICE', self.camera_id),
                                   ('OBSTIME', self.obstime)] + extra_headers)

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

    def save(self, basename=None, dirname='/data/acq_cameras', overwrite=False, compress=True,
             camera_ra=None, camera_dec=None, extra_headers=[]):

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

    def __init__(self, actor=None):

        self.actor = actor

        self.cameras = []
        self.connect_all()

        self.loop = None
        self._start_loop()

    def _start_loop(self):

        self.loop = task.LoopingCall(self._camera_check)
        self.loop.start(CAMERA_CHECK_LOOP_TIME)

    def _camera_check(self):
        """Checks connected cammeras and makes sure they are alive."""

        for camera_id in self.list_cameras():
            if camera_id not in self.get_camera_ids():
                if self.actor:
                    self.actor.writeToUsers('w', 'text="found camera {0}. '
                                                 'Connecting it."'.format(camera_id))
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

        self.cameras.append(MantaCamera(camera_id, actor=self.actor))

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

    @staticmethod
    def list_cameras():

        cameras = vimba.getCameraIds()
        return cameras


class MantaCamera(object):

    def __init__(self, camera_id, actor=None):

        self.actor = actor
        self._camera_type = None

        self._last_exposure = None

        self.init_camera(camera_id)

    def init_camera(self, camera_id):

        if camera_id not in vimba.getCameraIds():
            raise ValueError('camera_id {0} not found. Cameras found: {1}'
                             .format(camera_id, self.cameras))

        self.camera = vimba.getCamera(camera_id)

        self.camera.openCamera()
        self.set_default_config()

        self.open = True
        self.camera_id = camera_id

        self.frame0 = self.camera.getFrame()
        self.frame1 = self.camera.getFrame()

        self.frame0.announceFrame()
        self.camera.startCapture()

        if self.actor:
            self.actor.writeToUsers('i', 'text="connected {0}"'.format(camera_id))

    def get_other_frame(self, current_frame=None):

        for frame in self.frames:
            if frame is not current_frame:
                return frame

        return frame

    def set_default_config(self):

        self.camera.PixelFormat = 'Mono12'
        self.camera.ExposureTimeAbs = 1e6
        self.camera.AcquisionMode = 'SingleFrame'
        self.camera.GVSPPacketSize = 1500
        self.camera.GevSCPSPacketSize = 1500

    def expose(self):

        try:
            self.frame0.queueFrameCapture()
        except pymba.VimbaException:
            return False

        self.camera.runFeatureCommand('AcquisitionStart')
        self.camera.runFeatureCommand('AcquisitionStop')

        self.frame0.waitFrameCapture(int(self.camera.ExposureTimeAbs / 1e3) + 1000)

        img_buffer = self.frame0.getBufferByteData()
        img_data_array = np.ndarray(buffer=img_buffer,
                                    dtype=np.uint16,
                                    shape=(self.frame0.height,
                                           self.frame0.width))

        self._last_exposure = MantaExposure(img_data_array,
                                            self.camera.ExposureTimeAbs / 1e6,
                                            self.camera.cameraIdString)

        return self._last_exposure

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
        except pymba.VimbaException as ee:
            warnings.warn('failed closing the camera. Error: {0}'.format(str(ee)), BMOUserWarning)

        if self.actor:
            self.actor.writeToUsers('i', 'text="disconnected {0}"'.format(self.camera_id))

        self.open = False

    def __del__(self):
        """Destructor."""

        if self.open:
            self.close()
