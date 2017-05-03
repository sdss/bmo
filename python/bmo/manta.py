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

from distutils.version import StrictVersion

import astropy
import astropy.time
import astropy.io.fits as fits
import astropy.wcs as wcs

import numpy as np

from bmo.exceptions import BMOUserWarning
from bmo.utils import PIXEL_SIZE, FOCAL_SCALE

try:

    import pymba

    vimba = pymba.Vimba()
    vimba.startup()

    system = vimba.getSystem()

    if system.GeVTLIsPresent:
        system.runFeatureCommand('GeVDiscoveryAllOnce')
        time.sleep(0.2)

except OSError:

    vimba = None


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

        if compress:
            data_ext = fits.CompImageHDU(data=self.data)
        else:
            data_ext = fits.ImageHDU(data=self.data)

        primary = fits.PrimaryHDU(header=header)

        self.camera_ra = camera_ra or self.camera_ra
        self.camera_dec = camera_dec or self.camera_dec

        # Not the nicest way of doing this but it seems to be the safest one.
        if self.camera_ra is not None and self.camera_dec is not None:

            primary.header['RACAM'] = self.camera_ra
            primary.header['DECCAM'] = self.camera_dec

            # wcs_header = self.get_wcs_header(self.data.shape)
            # for key in wcs_header:
            #     data_ext.header[key] = wcs_header[key]

        hdulist = fits.HDUList([primary, data_ext])

        if overwrite is False:
            assert not os.path.exists(fn), \
                'the path exists. If you want to overwrite it use overwrite=True.'

        # Depending on the version of astropy, uses clobber or overwrite
        if StrictVersion(astropy.__version__) < StrictVersion('1.3.0'):
            hdulist.writeto(fn, clobber=overwrite)
        else:
            hdulist.writeto(fn, overwrite=overwrite)

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


class MantaCamera(object):

    def __init__(self, camera_id):

        self._last_exposure = None

        self.init_camera(camera_id)

    @staticmethod
    def list_cameras():

        cameras = vimba.getCameraIds()
        return cameras

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

    def close(self):
        """Ends capture and closes the camera."""

        try:
            self.camera.endCapture()
            self.camera.revokeAllFrames()
            self.camera.closeCamera()
            # self.vimba.shutdown()
        except pymba.VimbaException as ee:
            warnings.warn('failed closing the camera. Error: {0}'.format(str(ee)), BMOUserWarning)

        self.open = False

    def __del__(self):
        """Destructor."""

        if self.open:
            self.close()
