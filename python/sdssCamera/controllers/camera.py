#!/usr/bin/env python2
# encoding: utf-8
#
# camera.py
#
# Created by José Sánchez-Gallego on 12 Oct 2016.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import abc

from astropy.time import Time


def mjd():
    """Returns the current MJD, in the SDSS style."""

    return int(Time.now().mjd + 0.3)


class Camera(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self):

        self.name = None
        self.handler = None
        self._is_connected = False
        self._current_exposure_time = 1.

        self.image_prefix = '/data'
        self.seqno = 1

    @property
    def is_connected(self):
        """Returns True if the camera is connected and the link established."""

        return self._is_connected

    @property
    def exposure_time(self):
        """Gets the current exposure time, in seconds."""

        return self._current_exposure_time / 1000.

    @exposure_time.setter
    def exposure_time(self, value):
        """Sets the exposure time (in seconds) for all following exposures."""

        assert value > 0.005, 'Minimum exposure time is 5 ms.'
        self._current_exposure_time = float(value)

    def _check_connection(self):
        """Checks whether the camera is connected and connects it if it is not."""

        if not self.is_connected:
            self.connect()

    @abc.abstractmethod
    def connect(self):
        """Connects with the camera."""

        pass

    @abc.abstractmethod
    def get_camera_info(self):
        """Returns information about the camera."""

        pass

    @abc.abstractmethod
    def expose(self, exposure_time=None):
        """Exposes for ``exposure_time`` seconds and retrieves a numpy array.

        If ``exposure_time=None``, the default exposure time is used.

        """

        pass

    def save_image(self, ndarray, path=None, header=None):
        """Saves a numpy array as a FITS file.

        If ``path`` is not defined, the object ``image_prefix`` and ``seqno``
        will be used to create a unique path.

        If defined, header must be an
        ``astropy.io.fits.Header`` object or a dictionary that can be passed to
        ``Header``. If ``header=None``, a basic header will be added to the file
        containing exposure time, start time, and binning.

        """

        pass
