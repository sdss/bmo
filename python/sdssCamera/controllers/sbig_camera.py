#!/usr/bin/env python2
# encoding: utf-8
#
# sbig_camera.py
#
# Created by José Sánchez-Gallego on 13 Oct 2016.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import warnings

from functools import wraps

from .camera import Camera
from .sbig import SBIGCam


def _warning(message, category=UserWarning):
    print('{0}: {1}'.format(category.__name__, message))

warnings.showwarning = _warning


def check_connection(func):
    """Before doing anything, check if the camera is connected or connects it."""

    @wraps(func)
    def wrapper(inst, *args, **kwargs):
        if not inst.is_connected:
            inst.connect()
        return func(inst, *args, **kwargs)
    return wrapper


class SBIG(Camera):

    def __init__(self):

        super(SBIG, self).__init__()

        self.name = 'SBIG'
        self.handler = SBIGCam()

        self.seqno = self._init_seqno()

    def connect(self):
        """Connects with the camera."""

        if self.is_connected:
            warnings.warn('camera is already connected. Reconnecting.', UserWarning)

        self.handler.openDriver()
        self.handler.linkDevice()

        self._is_connected = True

    @check_connection
    def get_camera_type_string(self):
        """Gets the model of the camera."""

        print(self.handler.getCameraTypeString())

    @check_connection
    def get_camera_info(self, do_print=True):
        """Returns information about the camera."""

        params = self.handler.getCCDInfoParams()

        if do_print:

            print('Name:             {0}'.format(params['name']))
            print('Firmware version: {0}'.format(params['firmwareVersion']))
            print('Camera type:      {0}'.format(params['cameraType']))
            print('Readout modes:    {0}'.format(params['readoutModes']))

            readout_modes = [(mode['mode'], mode['width'], mode['height'],
                              mode['pixelWidth'], mode['pixelHeight'], mode['gain'])
                             for mode in params['readoutInfo']
                             if mode['width'] > 0 or mode['height'] > 0]

            print('Readout info:')
            for r_mode in sorted(readout_modes):
                print('    Mode:         {0}'.format(r_mode[0]))
                print('    Width:        {0}'.format(r_mode[1]))
                print('    Height:       {0}'.format(r_mode[2]))
                print('    Pixel width:  {0}'.format(r_mode[3]))
                print('    Pixel height: {0}'.format(r_mode[4]))
                print('    Gain:         {0}'.format(r_mode[5]))
                print()

        return params

    @check_connection
    def get_camera_name(self):
        """Returns information about the camera."""

        return self.handler.getCCDInfoParams()['name']

    def save_image(self, pImg, path=None):
        """Saves an image as a FITS file.

        If ``path`` is not defined, the object ``image_prefix`` and ``seqno``
        will be used to create a unique path.

        """

        ndarray = pImg.getNumpyArray()
        kwargs = {'exptime': pImg.getExposureTime(),
                  'binning': 1}

        super(SBIG, self).save_image(ndarray, path=path, **kwargs)

    @check_connection
    def expose(self, exposure_time=None, save=False, **kwargs):
        """Exposes for ``exposure_time`` seconds and retrieves a numpy array.

        If ``exposure_time=None``, the default exposure time is used. If ``save=True``,
        the image is saved as a FITS file. A ``path`` keyword argument can be passed
        with the file path where the image should be saved.

        """

        exposure_time = exposure_time or self.exposure_time
        assert exposure_time >= self.MIN_EXPOSURE_TIME, 'exposure time is too short.'

        pImg = self.handler.grabImage(expTime=exposure_time)

        if save:
            self.save_image(pImg, **kwargs)

        self.seqno += 1

        return pImg
