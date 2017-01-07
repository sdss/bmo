#!/usr/bin/env python
# encoding: utf-8
#
# file.py
#
# Created by José Sánchez-Gallego on 7 Jan 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import pymba
import numpy as np
import astropy.io.fits as fits
import time
import os


class MantaExposure(object):

    def __init__(self, data, exposure_time, camera_id):

        self.data = data
        self.exposure_time = np.round(exposure_time, 3)
        self.camera_id = camera_id

    def save(self, fn, overwrite=False):

        header = fits.Header({'EXPTIME': self.exposure_time,
                              'DEVICE': self.camera_id})
        hdulist = fits.HDUList([fits.PrimaryHDU(data=self.data, header=header)])

        if overwrite is False:
            assert not os.path.exists(fn), \
                'the path exists. If you want to overwrite it use overwrite=True.'

        hdulist.writeto(fn, overwrite=overwrite)


class MantaCamera(object):

    def __init__(self, camera_id=None):

        self.camera_id = camera_id
        self._last_exposure = None

        self.vimba = pymba.Vimba()
        self.vimba.startup()
        self.system = self.vimba.getSystem()
        self.system.runFeatureCommand('GeVDiscoveryAllOnce')

        self.cameras = self.vimba.getCameraIds()

        if camera_id:
            self.init_camera(camera_id)

    def init_camera(self, camera_id):

        if camera_id not in self.cameras:
            raise ValueError('camera_id {0} not found. Cameras found: {1}'
                             .format(camera_id, self.cameras))

        self.camera = self.vimba.getCamera(camera_id)

        self.camera.openCamera()
        self.set_default_config()

    def set_default_config(self):

        self.camera.PixelFormat = 'Mono12'
        self.camera.ExposureTimeAbs = 1e6
        self.camera.AcquisionMode = 'SingleFrame'

    def expose(self, exp_time=None):

        self.camera.AcquisionMode = 'SingleFrame'
        if exp_time:
            self.camera.ExposureTimeAbs = exp_time * 1e6

        frame = self.camera.getFrame()
        frame.announceFrame()
        frame.queueFrameCapture()

        self.camera.startCapture()

        self.camera.runFeatureCommand('AcquisitionStart')
        self.camera.runFeatureCommand('AcquisitionStop')

        time.sleep(self.camera.ExposureTimeAbs / 1e6 + 0.1)

        self.camera.endCapture()

        img_buffer = frame.getBufferByteData()
        img_data_array = np.ndarray(buffer=img_buffer,
                                    dtype=np.uint16,
                                    shape=(frame.height, frame.width)).copy()

        self.camera.revokeAllFrames()

        self._last_exposure = MantaExposure(img_data_array,
                                            self.camera.ExposureTimeAbs / 1e6,
                                            self.camera.cameraIdString)

        return self._last_exposure

    def save(self, fn, exposure=None, **kwargs):

        assert exposure is not None or self._last_exposure is not None, \
            'no exposure provided. Take an exposure before calling save.'

        exposure = exposure or self._last_exposure
        exposure.save(fn, **kwargs)

    def __del__(self):
        """Destructor."""

        self.camera.endCapture()
        self.camera.revokeAllFrames()
        self.vimba.shutdown()
