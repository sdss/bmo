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
import re

import astropy.table as table
import pyds9

from bmo.exceptions import BMOError

try:
    from sdss.internal.database.connections import LCODatabaseUserLocalConnection as db
    from sdss.internal.database.apo.platedb import ModelClasses as plateDB
except:
    db = None
    plateDB = None


__all__ = ('FOCAL_SCALE', 'PIXEL_SIZE', 'get_centroid', 'get_plateid',
           'get_off_camera_coords', 'get_translation_offset', 'get_rotation_offset',
           'show_in_ds9', 'read_ds9_regions', 'get_camera_coordinates')

FOCAL_SCALE = 3600. / 330.275  # arcsec / mm
PIXEL_SIZE = 5.86 / 1000.  # in mm

DEFAULT_IMAGE_SHAPE = (1936, 1216)


def get_plateid(cartID):
    """Gets the plateID for a certain cartID."""

    if db is None:
        raise BMOError('no database is available.')

    session = db.Session()

    return session.query(plateDB.Plate.plate_id).join(plateDB.Plugging,
                                                      plateDB.ActivePlugging).filter(
        plateDB.ActivePlugging.pk == cartID).one()[0]


def get_camera_coordinates(plate_id):
    """Returns the RA/Dec coordinates for both cameras."""

    if db is None:
        raise BMOError('no database is available.')

    session = db.Session()

    plate = session.query(plateDB.Plate).filter(plateDB.Plate.plate_id == plate_id).scalar()

    if plate is None:
        raise BMOError('plate {0} not found.'.format(plate_id))

    on_ra = plate.plate_pointings[0].pointing.center_ra
    on_dec = plate.plate_pointings[0].pointing.center_dec

    off_coords = get_off_camera_coords(plate_id)

    return [(float(on_ra), float(on_dec)), (off_coords[2], off_coords[3])]


def get_off_camera_coords(plate_id):
    """Returns the coordinates for the off-axis camera."""

    data = table.Table.read(
        os.path.join(os.path.dirname(__file__), '../../etc/off-axis.dat'),
        format='ascii.commented_header')

    if plate_id not in data['Plate']:
        return None
    else:
        row = data[data['Plate'] == plate_id][0]
        return (row['xFocal'], row['yFocal'], row['RA'], row['DEC'])


def get_centroid(image):
    """Uses PyGuide to return the brightest centroid in an array."""

    mask = np.zeros(image.shape)

    ccdInfo = PyGuide.CCDInfo(np.median(image), 5, 5)
    stars = PyGuide.findStars(image, mask, None, ccdInfo)

    centroids = stars[0]
    assert len(centroids) > 0, 'no centroids found.'

    return centroids[0]


def get_translation_offset(centroid, shape=DEFAULT_IMAGE_SHAPE):
    """Calculates the offset from the centre of the image to the centroid.

    The offset signs are selected so that the returned offset is the one the
    telescope needs to apply to centre the star.

    Parameters:
        centroid (tuple):
            A tuple containing the x and y coordinates of the centroid to
            be centred, in image pixels.
        shape (tuple):
            The width and height of the original image, to determine the centre
            of the field.

    Returns:
        trans_ra, tans_dec:
            Returns a tuple with the translation in RA and Dec, respectively,
            that needs to be applied to centre the centroid/star.


    """

    on_centre = np.array([shape[0] / 2., shape[1] / 2.])
    on_centroid = np.array(centroid)

    trans_ra, trans_dec = (on_centroid - on_centre) * PIXEL_SIZE * FOCAL_SCALE

    return trans_ra, trans_dec


def get_rotation_offset(plate_id, centroid, shape=DEFAULT_IMAGE_SHAPE, translation_offset=None):
    """Calculates the rotation offset.

    The offset signs are selected so that the returned offset is the one the
    telescope needs to apply to centre the star.

    Parameters:
        plate_id (int):
            The plate_id, used to determine the position of the off-axis camera
            on the plate.
        centroid (tuple):
            A tuple containing the x and y coordinates of the centroid to be
            centred, in image pixels.
        shape (tuple):
            The width and height of the original image, to determine the centre
            of the field.
        translation_offset (tuple or None):
            The ``(RA, Dec)`` translation offset in arcsec, as calculated by
            ``get_translation_offset``, to be applied before calculating the
            rotation offset. If ``None``, no translation offset will be
            applied.

    Returns:
        rotation:
            Returns the rotation, in arcsec, that needs to be applied to centre
            the centroid/star.


    """

    def get_angle(x_focal, y_focal):
        """Returns the angle from the centre of the plate."""

        x_focal_rad = np.deg2rad(x_focal * FOCAL_SCALE / 3600)
        y_focal_rad = np.deg2rad(y_focal * FOCAL_SCALE / 3600)

        cc = np.arccos(np.cos(x_focal_rad) * np.cos(y_focal_rad))
        return np.rad2deg(np.arccos(np.tan(np.pi / 2. - cc) * np.tan(y_focal_rad)))

    centroid = np.array(centroid)
    shape = np.array(shape)

    off_coords = get_off_camera_coords(plate_id)
    xy_focal = off_coords[0:2]
    if not xy_focal:
        raise ValueError('cannot determine the x/yFocal of the off-axis camera for this plate. '
                         'The rotation offset cannot be calculated.')
    else:
        x_focal_centre, y_focal_centre = xy_focal

    angle_centre = get_angle(x_focal_centre, y_focal_centre)

    if translation_offset:
        translation_offset_pix = np.array(translation_offset) / FOCAL_SCALE / PIXEL_SIZE
        centroid -= translation_offset_pix

    # Calculates the x/yFocal of the cetroid.
    img_centre = shape / 2.
    x_pix, y_pix = centroid - img_centre

    x_focal_off = x_focal_centre - x_pix * PIXEL_SIZE
    y_focal_off = y_focal_centre + y_pix * PIXEL_SIZE

    angle_off = get_angle(x_focal_off, y_focal_off)

    rotation = (angle_centre - angle_off) * 3600

    return rotation


def show_in_ds9(image, frame=1, ds9=None):
    """Displays an image in DS9, calculating star centroids.

    Parameters:
        image (Numpy ndarray):
            A Numpy ndarray containing the image to display.
        frame (int):
            The frame in which the image will be displayed.
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

    if not isinstance(ds9, pyds9.DS9):
        if ds9 is None:
            raise ValueError('no DS9 connection available. Have you run bmo ds9 connect?')
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

    ds9.set('frame {0}'.format(frame))
    ds9.set_np2arr(image)
    ds9.set('zoom to fit')

    ds9.set('regions command {{point({0}, {1}) # point=cross 20, color=blue}}'.format(
        image.shape[1] / 2., image.shape[0] / 2.))

    if centroid:
        ds9.set('regions command {{circle({0}, {1}, {2}) # color=green}}'.format(xx, yy, rad))
        return (xx, yy, rad)

    return None


def read_ds9_regions(ds9, frame=1):
    """Reads regions from DS9 and returns the region centre and image dimensions."""

    ds9.set('frame {0}'.format(frame))
    regions = ds9.get('regions -format ds9 -system image')

    n_circles = regions.count('circle')
    if n_circles == 0:
        return False, 'no circle regions detected in frame {0}'.format(frame)
    elif n_circles > 1:
        return False, 'multiple circle regions detected in frame {0}'.format(frame)

    circle_match = re.match('.*circle\((.*)\)', regions, re.DOTALL)

    if circle_match is None:
        return False, 'cannot parse region in frame {0}'.format(frame)

    try:
        xx, yy = map(float, circle_match.groups()[0].split(',')[0:2])
    except Exception as ee:
        return False, 'problem found while parsing region for frame {0}: {1!r}'.format(frame, ee)

    try:
        height = int(ds9.get('fits height'))
        width = int(ds9.get('fits width'))
    except Exception as ee:
        return False, 'problem found while getting shape for frame {0}: {1!r}'.format(frame, ee)

    return True, (xx, yy, width, height)
