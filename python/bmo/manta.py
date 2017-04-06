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

from distutils.version import StrictVersion

import astropy
import astropy.io.fits as fits
import numpy as np

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

    def __init__(self, data, exposure_time, camera_id):

        self.data = data
        self.exposure_time = np.round(exposure_time, 3)
        self.camera_id = camera_id

        self.header = fits.Header([('EXPTIME', self.exposure_time),
                                   ('DEVICE', self.camera_id)])

    def save(self, fn, overwrite=False):

        hdulist = fits.HDUList([fits.PrimaryHDU(data=self.data, header=self.header)])

        if overwrite is False:
            assert not os.path.exists(fn), \
                'the path exists. If you want to overwrite it use overwrite=True.'

        # Depending on the version of astropy, uses clobber or overwrite
        if StrictVersion(astropy.__version__) < StrictVersion('1.3.0'):
            hdulist.writeto(fn, clobber=overwrite)
        else:
            hdulist.writeto(fn, overwrite=overwrite)

    @classmethod
    def from_fits(cls, fn):

        hdulist = fits.open(fn)
        new_object = MantaCamera.__new__(cls)

        new_object.data = hdulist[0].data
        new_object.header = hdulist[0].header
        new_object.camera_id = hdulist[0].header['DEVICE']
        new_object.exposure_time = float(hdulist[0].header['EXPTIME'])

        return new_object


class MantaCamera(object):

    def __init__(self, camera_id=None):

        self.open = True

        self.camera_id = camera_id
        self._last_exposure = None

        self.cameras = vimba.getCameraIds()

        if camera_id not in self.cameras:
            raise ValueError('camera_id {0} not found. Cameras found: {1}'
                             .format(camera_id, self.cameras))

        if camera_id:
            self.init_camera(camera_id)

    @staticmethod
    def list_cameras():

        cameras = vimba.getCameraIds()
        return cameras

    def init_camera(self, camera_id):

        if camera_id not in self.cameras:
            raise ValueError('camera_id {0} not found. Cameras found: {1}'
                             .format(camera_id, self.cameras))

        self.camera = vimba.getCamera(camera_id)

        self.camera.openCamera()
        self.set_default_config()

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

    def close(self):
        self.camera.endCapture()
        self.camera.revokeAllFrames()
        # self.vimba.shutdown()

        self.open = False

    def __del__(self):
        """Destructor."""

        if self.open:
            self.close()
