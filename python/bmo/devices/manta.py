#!/usr/bin/env python
# encoding: utf-8
#
# manta.py
#
# Created by José Sánchez-Gallego on 7 Jan 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import time
import warnings

from twisted.internet import task

from distutils.version import StrictVersion

import astropy
import astropy.time
import astropy.io.fits as fits
import astropy.wcs

import numpy as np

import bmo

from bmo.exceptions import BMOUserWarning, BMOMissingImportWarning, MantaError
from bmo.devices.fake_vimba import Vimba as FakeVimba
from bmo.logger import log
from bmo.utils import PIXEL_SIZE, FOCAL_SCALE

from twistedActor.device import expandUserCmd

try:
    from astropy.stats import SigmaClip
    from photutils.background import Background2D, MedianBackground
    sigma_clip = SigmaClip(sigma=bmo.config['image']['background']['sigma_clip']['sigma'],
                           iters=bmo.config['image']['background']['sigma_clip']['iters'])
    bkg_estimator = MedianBackground()
except Exception:
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

    def __init__(self, raw, exposure_time, camera_id, extra_headers=[]):

        self._raw = raw
        self._data = None

        self._background = None

        self.exposure_time = np.round(exposure_time, 3)
        self.camera_id = camera_id
        self.obstime = astropy.time.Time.now().isot

        self.hole_ra = None
        self.hole_dec = None

        self.header = fits.Header([('EXPTIME', self.exposure_time),
                                   ('DEVICE', self.camera_id),
                                   ('OBSTIME', self.obstime)] + extra_headers)

    @property
    def raw(self):
        """Returns the raw image."""

        return self._raw

    @property
    def data(self):
        """Returns the image (defaults to raw)."""

        if self._data is None:
            return self.raw
        else:
            return self._data

    @data.setter
    def data(self, value):
        """Sets the data."""

        self._data = value

    @property
    def background(self):
        """Returns the value of background."""

        return self._background

    @background.setter
    def background(self, value):
        """Sets the value of background."""

        if value is None:
            self._background = None
        else:
            assert isinstance(value, Background2D), 'background must be a Background2D object'
            self._background = value

    def subtract_background(self, background=None, sigma_clip=sigma_clip,
                            bkg_estimator=bkg_estimator, box_size=(50, 50),
                            filter_size=(3, 3)):
        """Fits a 2D background."""

        if self.background is not None:
            raise ValueError('background has already been subtracted.')

        if Background2D is None:
            raise ImportError('photutils has not been installed.', BMOUserWarning)

        if background is None:
            self.background = Background2D(self.data, box_size, filter_size=filter_size,
                                           sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
        else:
            self.background = background

        self.data = self.data.astype(np.float64) - self.background.background

        return self.background

    def set_hole_radec(self, ra, dec):
        """Sets the RA and Dec of the centre of the image."""

        self.hole_ra = ra
        self.hole_dec = dec

    def get_wcs_header(self, shape):
        """Returns an WCS header for an image of a certain ``shape``.

        It assumes the centre of the image corresponds to ``ra, dec``.

        """

        if self.hole_ra is None or self.hole_dec is None:
            warnings.warn('RA/Dec not set for the image. '
                          'Cannot generate astrometric solution.', BMOUserWarning)
            return []

        ww = astropy.wcs.WCS(naxis=2)
        ww.wcs.crpix = [shape[1] / 2., shape[0] / 2]
        ww.wcs.cdelt = np.array([FOCAL_SCALE * PIXEL_SIZE, FOCAL_SCALE * PIXEL_SIZE]) / 3600.
        ww.wcs.crval = [self.hole_ra, self.hole_dec]
        ww.wcs.ctype = ['RA---TAN', 'DEC--TAN']

        return ww.to_header()

    def get_background_cards(self):
        """Returns a list of header values describing the background model."""

        cards = fits.Header([
            ('BACKGR', False, 'Was a background subtracted?'),
            ('SIGMA', '', 'The sigma value used for sigma clipping'),
            ('SIGMAIT', '', 'The number of iterations for sigma clipping'),
            ('BACKBOXX', '', 'The box size along axis x'),
            ('BACKBOXY', '', 'The box size along axis y'),
            ('BACKFILX', '', 'The window size of the 2D median filter along x'),
            ('BACKFILY', '', 'The window size of the 2D median filter along y')
        ])

        if not self.background:
            cards['BACKGR'] = False
            return cards

        cards['BACKGR'] = True
        cards['SIGMA'] = sigma_clip.sigma
        cards['SIGMAIT'] = sigma_clip.iters
        cards['BACKBOXX'] = self.background.box_size[0]
        cards['BACKBOXY'] = self.background.box_size[1]
        cards['BACKFILX'] = self.background.filter_size[0]
        cards['BACKFILY'] = self.background.filter_size[1]

        return cards

    def save(self, basename=None, dirname='/data/bcam', overwrite=False,
             compress=True, wcs=None):
        """Saves the image to disk.

        Parameters:
            basename (str or None):
                The name of the image to save. If ``None``, a name will be
                given to the image based on the camera ID and the time.
            dirname (str):
                The path to where to save the image.
            overwrite (bool):
                If ``True``, overwrites the destination path, if it exists.
            compress (bool):
                If ``True``, the image will be compressed using
                `fpack <http://docs.astropy.org/en/latest/io/fits/usage/unfamiliar.html#astropy-io-fits-compressedimagedata>`__,
                and a ``.fz`` suffix will be added to the path.
            wcs (`astropy.wcs.WCS` object):
                The astrometry solution for the image as an `astropy.wcs.WCS`
                object. If ``wcs=None``, an approximate WCS solution will be
                generated using the centre of the image and the camera pixel
                scale.

        """

        if basename is None:
            timestr = time.strftime('%d%m%y_%H%M%S')
            basename = '{0}_{1}.fits'.format(self.camera_id, timestr)

        fn = os.path.join(dirname, basename)

        primary = fits.PrimaryHDU(data=self.data, header=self.header)

        primary.header['HOLERA'] = self.hole_ra if self.hole_ra else ''
        primary.header['HOLEDEC'] = self.hole_dec if self.hole_dec else ''

        # Creates the WCS header and adds it to the primary HDU.
        if wcs is not None:
            assert isinstance(self.wcs, astropy.wcs.WCS), 'invalid type for wcs.'
            wcs_header = wcs.to_header()
        else:
            try:
                wcs_header = self.get_wcs_header(self.data.shape)
            except Exception as error:
                warnings.warn('failed to create WCS header: {}'.format(error),
                              BMOUserWarning)

        primary.header.extend(wcs_header)

        # Adds cards for the background model
        primary.header.extend(self.get_background_cards())

        hdu = primary

        if overwrite is False:
            assert not os.path.exists(fn), \
                'the path exists. If you want to overwrite it use overwrite=True.'

        if compress:
            fn += '.fz'
            hdu = fits.CompImageHDU(data=hdu.data,
                                    header=hdu.header)

        # Depending on the version of astropy, uses clobber or overwrite
        if StrictVersion(astropy.__version__) < StrictVersion('1.3.0'):
            hdu.writeto(fn, clobber=overwrite)
        else:
            hdu.writeto(fn, overwrite=overwrite)

        del hdu

        return fn

    @classmethod
    def from_fits(cls, fn):
        """Creates a ``MantaExposure`` object from a FITS file."""

        hdulist = fits.open(fn)
        header = hdulist[0].header

        new_object = MantaCamera.__new__(cls)

        new_object.data = hdulist[0].data
        new_object.header = header
        new_object.camera_id = header['DEVICE']
        new_object.exposure_time = float(header['EXPTIME'])
        new_object.obstime = header['OBSTIME']

        new_object.hole_ra = header['HOLERA']
        new_object.hole_dec = header['HOLEDEC']

        if header['BACKGR'] is True:
            image_sigma_clip = SigmaClip(sigma=header['SIGMA'],
                                         iters=header['ITERS'])

            box_size = (header['BACKBOXX'], header['BACKBOXY'])
            filter_size = (header['BACKFILX'], header['BACKFILY'])

            new_object.background = Background2D(new_object.data, box_size,
                                                 filter_size=filter_size,
                                                 sigma_clip=image_sigma_clip,
                                                 bkg_estimator=bkg_estimator)

            new_object._raw = new_object.data + new_object.background.background

        return new_object


class MantaCameraSet(object):
    """A set of Manta cameras.

    This class allows to control a set of cameras (at this point, an on-axis
    and and off-axis). It handles the Vimba main API and the Vimba system
    controller, and allows to list cameras, connect, and disconnect them.

    Parameters:
        vimba (``pymba.Vimba`` object):
            A ``pymba.Vimba()`` object, that will be used to talk to
            the Vimba API.
        actor:
            The BMO actor, or ``None``. If the latter, no messages will be
            written to the users.

    """

    def __init__(self, vimba, actor=None):

        self.actor = actor

        self.vimba = vimba
        log.debug('starting MantaCameraSet with vimba={!r}'.format(vimba))

        self.system = None

        self._init_controller()

        self.cameras = []
        self.connect_all()

        # Starts the loop that checks whether cameras are connected or disconnected.
        self.loop = None
        self._start_loop()

    def _init_controller(self):
        """Initialises the camera controller."""

        self.vimba.startup()

        self.system = self.vimba.getSystem()

        if self.system.GeVTLIsPresent:
            # THis automatically tells the vimba API when a camera appears.
            self.system.runFeatureCommand('GeVDiscoveryAllAuto')
            time.sleep(0.2)

        log.debug('Vimba system started.')

    def _start_loop(self):
        """Starts a loop to check whether the cameras have changed."""

        self.loop = task.LoopingCall(self._camera_check)

        # Overrides UPDATE_INTERVAL from the config file, if possible.
        if self.actor and 'update_interval' in self.actor.config['cameras']:
            self.loop.start(self.actor.config['cameras']['update_interval'])
        else:
            warnings.warn('cannot find update_interval in actor config. '
                          'Using default value for update camera interval.',
                          BMOUserWarning)
            self.loop.start(UPDATE_INTERVAL)

    def _camera_check(self):
        """Checks connected cammeras and makes sure they are alive."""

        # The camera list, as reported by the Vimba API.
        cameras_now = self.list_cameras()

        for camera_id in cameras_now:
            if camera_id not in self.get_camera_ids():
                log.info('found camera {0}. Connecting it.'.format(camera_id), self.actor)
                self.connect(camera_id)
                return

        for camera_id in self.get_camera_ids():
            if camera_id not in cameras_now:
                self.disconnect(camera_id)
                return

    def update_keywords(self, user_cmd=None):
        """Outputs camera keywords."""

        update_cmd = expandUserCmd(user_cmd)

        if self.actor is None:
            warnings.warn('MantaCameraSet initiated without actor. Cannot output keywords.',
                          BMOUserWarning)
            update_cmd.setState(update_cmd.Failed)
            return update_cmd

        camera_connected = [False, False]
        camera_device = ['', '']
        camera_state = ['idle', 'idle']

        for camera in self.cameras:
            camera_idx = 0 if camera.camera_type == 'on' else 1
            camera_connected[camera_idx] = True
            camera_device[camera_idx] = camera.camera_id
            camera_state[camera_idx] = camera.state

        self.actor.writeToUsers('i', 'bmoCamera="{}","{}","{}","{}"'.format(camera_connected[0],
                                                                            camera_connected[1],
                                                                            camera_device[0],
                                                                            camera_device[1]))

        self.actor.writeToUsers('i', 'bmoExposeState="{}","{}"'.format(camera_state[0],
                                                                       camera_state[1]))

        controller_state = 'Fake' if isinstance(self.vimba, FakeVimba) else self.vimba.getVersion()
        self.actor.writeToUsers('i', 'bmoVimbaVersion="{}"'.format(controller_state))

        log.debug('updated camera keywords.', actor=False)

        update_cmd.setState(update_cmd.Done)

        return update_cmd

    def connect(self, camera_id):
        """Connects a camera."""

        if camera_id not in self.list_cameras():
            raise ValueError('camera {0} is not connected'.format(camera_id))

        camera = MantaCamera(camera_id, self.vimba, camera_set=self, actor=self.actor)

        self.cameras.append(camera)

        if self.actor:
            self.update_keywords()

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

        if self.actor:
            self.update_keywords()

    def get_camera_ids(self):
        """Returns a list of connected camera ids."""

        return [camera.camera_id for camera in self.cameras]

    def list_cameras(self):
        """Returns a list of connected camera IDs."""

        cameras = self.vimba.getCameraIds()
        return cameras

    def close(self):
        """Closes the Vimba system."""

        for camera in self.cameras:
            camera.close()

        log.info('shutting down the Vimba system.', self.actor)
        self.vimba.shutdown()

    def __del__(self):
        """Closes the Vimba system if the object is destroyed."""

        self.close()


class MantaCamera(object):
    """A class representing a Manta camera.

    This class allows to connect a Manta camera and expose asynchronously.

    Parameters:
        camera_id (str):
            The camera ID of the camera to connect.
        vimba (``pymba.Vimba`` object):
            A ``pymba.Vimba()`` object, that will be used to talk to
            the Vimba API. Normally passed down by ``MantaCameraSet``.
        camera_set (``MantaCameraSet`` object or None):
            The parent ``MantaCameraSet`` object to which this camera belongs
            to.
        actor:
            The BMO actor, or ``None``. If the latter, no messages will be
            written to the users.

    """

    def __init__(self, camera_id, vimba, camera_set=None, actor=None):

        log.info('connecting camera {!r}'.format(camera_id), actor)

        self.actor = actor

        self.vimba = vimba
        self.camera_set = camera_set

        self._state = 'idle'
        self.is_busy = False
        self._exposure_cb = None  # The function that will be call when and exposure is done.

        self.camera = None
        self._camera_type = None

        self._last_exposure = None
        self.background = None

        self.init_camera(camera_id)

    def init_camera(self, camera_id):
        """Initialises the camera.

        Gets the camera from the Vimba API, opens it, and sets the default
        configuration. It then creates a frame and announces and queues it
        to the camera. Finally, starts the capture mode.

        """

        if camera_id not in self.vimba.getCameraIds():
            raise ValueError('camera_id {0} not found. Cameras found: {1}'
                             .format(camera_id, self.cameras))

        self.camera = self.vimba.getCamera(camera_id)

        self.camera.openCamera()
        log.debug('camera open.')

        self.set_default_config()
        log.debug('default configuration loaded.')

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
        """Sets the default configuration."""

        self.camera.PixelFormat = 'Mono12'
        self.camera.ExposureTimeAbs = 1e6
        self.camera.AcquisionMode = 'SingleFrame'
        self.camera.GVSPPacketSize = 1500
        self.camera.GevSCPSPacketSize = 1500

    def expose(self, call_back_func=None):
        """Exposes the camera.

        Accepts a ``call_back_func`` function to be called with the resulting
        exposure.

        """

        if self.is_busy:
            raise MantaError('camera is busy. Cannot expose now.')

        self._exposure_cb = call_back_func

        log.debug('starting exposure.', actor=False)

        self.camera.runFeatureCommand('AcquisitionStart')
        self.camera.runFeatureCommand('AcquisitionStop')

    def frame_callback(self, frame):
        """Frame callback that gets caled when the frame is filled.

        This callback is called when ``ExposureTimeAbs`` has passed and the
        frame is filled. It retrieves the image data and creates a
        ``MantaExposure`` object. It then requeues the frame for future use.

        If ``MantaCamera.exposure`` has been called with a ``call_back_func``,
        it calls that function and passes it the ``MantaExposure`` object.

        """

        # log.debug('frame callback called. Processing image.')

        img_buffer = frame.getBufferByteData()
        img_data_array = np.ndarray(buffer=img_buffer,
                                    dtype=np.uint16,
                                    shape=(frame.height, frame.width))

        self._last_exposure = MantaExposure(img_data_array,
                                            self.camera.ExposureTimeAbs / 1e6,
                                            self.camera.cameraIdString)

        self.frame.queueFrameCapture(self.frame_callback)
        # log.debug('requeued frame.')

        self.is_busy = False

        if self._exposure_cb is not None:
            # log.debug('calling exposure callback function.')
            self._exposure_cb(self._last_exposure)

        return

    def save(self, fn, exposure=None, **kwargs):
        """Saves a ``MantaExposure`` to disk.

        Parameters:
            fn (str):
                The path to where to save the image.
            exposure (``MantaExposure`` object or None):
                A ``MantaExposure`` object to save. If ``None``, the last`
                exposure will be saved.
            kwargs (dict):
                Keyword arguments to be passed to ``MantaExposure.save``.

        """

        assert exposure is not None or self._last_exposure is not None, \
            'no exposure provided. Take an exposure before calling save.'

        exposure = exposure or self._last_exposure
        exposure.save(fn, **kwargs)

    def reconnect(self):
        """Closes and reconnects the camera."""

        self.close()
        self.init_camera(self.camera_id)

    @property
    def state(self):
        """Returns the state of the camera."""

        return self._state

    @state.setter
    def state(self, value):
        """Sets the state of the camera and updated keywords."""

        assert value in ['exposing', 'idle']
        self._state = value

        if self.camera_set is not None and self.camera_set.actor is not None:
            self.camera_set.update_keywords()

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

        if self.open is False:
            warnings.warn('the camera is not open.', BMOUserWarning)
            return

        log.debug('closing camera {!r}'.format(self.camera_id), self.actor)

        try:
            self.camera.flushCaptureQueue()
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
