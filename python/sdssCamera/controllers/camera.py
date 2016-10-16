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
import glob
import os
import re

from astropy.io import fits
from astropy.time import Time, TimeDelta


def mjd():
    """Returns the current MJD, in the SDSS style."""

    return int(Time.now().mjd + 0.3)


class CameraError(Exception):
    pass


class Camera(object):

    __metaclass__ = abc.ABCMeta

    MIN_EXPOSURE_TIME = 0.005

    def __init__(self):

        self.handler = None
        self.name = 'camera'
        self._is_connected = False
        self._current_exposure_time = 1.

        self.image_prefix = '/data/acq_cameras'
        self.seqno = self._init_seqno()

        self._abort_multi_exposure = False

    def _init_seqno(self):
        """Sets seqno with the latest unused seqno in the default directory."""

        full_path = os.path.join(self.image_prefix, self.name.lower(), str(mjd()))
        if not os.path.exists(full_path):
            return 1

        files = glob.glob(os.path.join(full_path, '{0}_*.fits'.format(self.name.lower())))
        if len(files) == 0:
            return 1

        pattern = r'({0}_)([0-9]+)'.format(self.name.lower())
        nex_seqno = max([int(re.search(pattern, fn).group(2)) for fn in files]) + 1

        return nex_seqno

    @property
    def is_connected(self):
        """Returns True if the camera is connected and the link established."""

        return self._is_connected

    @property
    def exposure_time(self):
        """Gets the current exposure time, in seconds."""

        return self._current_exposure_time

    @exposure_time.setter
    def exposure_time(self, value):
        """Sets the exposure time (in seconds) for all following exposures."""

        min_exptime = self.MIN_EXPOSURE_TIME
        assert value > min_exptime, 'Minimum exposure time is {0} seconds.'.format(min_exptime)
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
    def expose(self, exposure_time=None, save=False):
        """Exposes for ``exposure_time`` seconds and retrieves a SBIG image object.

        If ``exposure_time=None``, the default exposure time is used. If ``save=True``,
        the image is saved as a FITS file.

        """

        pass

    def multi_expose(self, n_exposures=0, **kwargs):
        """Takes ``n_exposures``. If ``n_exposures="""

        pass

    @abc.abstractmethod
    def save_image(self, ndarray, path=None, header=None, **kwargs):
        """Saves a numpy array as a FITS file.

        If ``path`` is not defined, the object ``image_prefix`` and ``seqno``
        will be used to create a unique path.

        If defined, header must be an
        ``astropy.io.fits.Header`` object or a dictionary that can be passed to
        ``Header``. If ``header=None``, a basic header will be added to the file
        containing exposure time, start time, and binning.

        Returns the ``HDUList`` for the image.

        This is a prototype method that should be super'd by concrete methods
        by passing the numpy array and a list of keywords with header keywords
        to override.


        """

        needed_keywords = ['exptime', 'binning']

        assert not header or isinstance(header, (fits.Header, dict)), \
            'header must be a dict or a fits.Header'

        if header:
            header = fits.Header(header)
        else:
            header = fits.Header()

        for keyword in needed_keywords:
            if keyword not in header:
                value = kwargs.pop(keyword, None)
                if value is None:
                    raise CameraError('{0} is not defined in header'.format(keyword))
                header[keyword] = value

        # If obstime is not defined, calculates it as the current time minus the exposure time.
        if 'obstime' not in header:
            obstime = (Time.now() - TimeDelta(header['exptime'], format='sec')).isot
            header['obstime'] = obstime

        if path is None:
            path = os.path.join(self.image_prefix, self.name.lower(), str(mjd()),
                                '{0}_{1:04d}.fits'.format(self.name.lower(), self.seqno))

        path_dir = os.path.dirname(path)
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)

        hdu = fits.PrimaryHDU(data=ndarray, header=header)
        hdu_list = fits.HDUList([hdu])

        hdu_list.writeto(path)

        return hdu_list
