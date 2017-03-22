#!/usr/bin/env python
# encoding: utf-8
#
# utils.py
#
# Created by José Sánchez-Gallego on 6 Jan 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import PyGuide
import numpy as np
import os

import astropy.table as table
import pyds9


FOCAL_SCALE = 3600. / 330.275  # arcsec / mm
PIXEL_SIZE = 5.86 / 1000.  # in mm


def get_plateid(cartID):
    """Gets the plateID for a certain cartID."""

    from sdss.internal.database.connections import LCODatabaseUserLocalConnection as db
    from sdss.internal.database.apo.platedb import ModelClasses as plateDB

    session = db.Session()

    return session.query(plateDB.Plate.plate_id).join(plateDB.Plugging,
                                                      plateDB.ActivePlugging).filter(
        plateDB.ActivePlugging.pk == cartID).one()[0]


def get_xyfocal_off_camera(plateID):
    """Returns the x/yfocal for the off-axis camera."""

    data = table.Table.read(
        os.path.join(os.path.dirname(__file__), '../../etc/off-axis.dat'),
        format='ascii.commented_header')

    if plateID not in data['Plate']:
        return None
    else:
        row = data[data['Plate'] == plateID]
        return row['xFocal'][0], row['yFocal'][0]


def get_centroid(image):
    """Uses PyGuide to return the brightest centroid in an array."""

    mask = np.zeros(image.shape)

    ccdInfo = PyGuide.CCDInfo(np.median(image), 5, 5)
    stars = PyGuide.findStars(image, mask, None, ccdInfo)

    centroids = stars[0]
    assert len(centroids) > 0, 'no centroids found.'

    return centroids[0]


def show_in_ds9(image, camera_type, ds9=None):
    """Displays an image in DS9, calculating star centroids.

    Parameters:
        image (Numpy ndarray):
            A Numpy ndarray containing the image to display.
        camera_type ({'on_axis', 'off_axis'}):
            The type of camera image being displayed.
        ds9 (pyds9 object or None or str):
            Either a ``pyds9`` object used to communicate with DS9, a string to
            be used to create such a connection, or ``None``. In the latter
            case ``pyds9.DS9`` will be called without arguments.

    Returns:
        result (None or tuple):
            If no centroid has been found for the image, returns ``None``.
            Otherwise, returns a tuple with the x, y position of the centroid,
            and the radius, as detected by PyGuide.

    Example:
        Opens a FITS file and displays it
          >>> data = fits.getdata('image.fits')
          >>> centroid = show_in_ds9(data, 'on_axis')
          >>> print(centroid)
          >>> (19.2, 145.1, 5.1)

    """

    assert camera_type in ['on_axis', 'off_axis']

    if not isinstance(ds9, pyds9.DS9):
        if ds9 is None:
            ds9 = pyds9.DS9()
        elif isinstance(ds9, str):
            ds9 = pyds9.DS9(ds9)
        else:
            raise ValueError('incorrect value for ds9 keyword: {0!r}'.format(ds9))

    try:
        centroid = get_centroid(image)
        xx, yy = centroid.xyCtr
        rad = centroid.rad
    except AssertionError:
        centroid = None

    frame = 1 if camera_type == 'on_axis' else 2

    ds9.set('frame {0}'.format(frame))
    ds9.set_np2arr(image)
    ds9.set('zoom to fit')

    ds9.set('regions command {{point({0}, {1}) # point=cross 20, color=blue}}'.format(
        image.shape[1] / 2., image.shape[0] / 2.))

    if centroid:
        ds9.set('regions command {{circle({0}, {1}, {2}) # color=green}}'.format(xx, yy, rad))
        return (xx, yy, rad)

    return None
