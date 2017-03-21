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

import matplotlib.pyplot as plt


focal_scale = 3600. / 330.275  # arcsec / mm
pixel_size = 5.86 / 1000.  # in mm


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

    mask = np.zeros(image.shape)

    ccdInfo = PyGuide.CCDInfo(np.median(image), 5, 5)
    stars = PyGuide.findStars(image, mask, None, ccdInfo)

    centroids = stars[0]
    assert len(centroids) > 0, 'no centroids found.'

    return centroids[0]


def calculate_translation_offset(onaxis, offaxis, plot=False):

    onaxis_centroid = get_centroid(onaxis)
    offaxis_centroid = get_centroid(offaxis)

    print('On-axis centroid: ', onaxis_centroid)
    print()
    print('Off-axis centroid: ', offaxis_centroid)

    if plot:

        fig, axes = plt.subplots(2, sharex=True)

        axes[0].imshow(onaxis, origin='lower', cmap='gist_heat')
        axes[0].scatter(onaxis_centroid.xyCtr[0], onaxis_centroid.xyCtr[1],
                        s=50, marker='x', c='b')
        axes[0].vlines(onaxis.shape[1] / 2, 0, onaxis.shape[0], colors=['y'], lw=1)
        axes[0].hlines(onaxis.shape[0] / 2, 0, onaxis.shape[1], colors=['y'], lw=1)

        axes[1].imshow(offaxis, origin='lower', cmap='gist_heat')
        axes[1].scatter(offaxis_centroid.xyCtr[0], offaxis_centroid.xyCtr[1],
                        s=50, marker='x', c='b')
        axes[1].vlines(offaxis.shape[1] / 2, 0, offaxis.shape[0], colors=['y'], lw=1)
        axes[1].hlines(offaxis.shape[0] / 2, 0, offaxis.shape[1], colors=['y'], lw=1)

        plt.xlim(0, onaxis.shape[1])
        plt.ylim(0, offaxis.shape[0])

        plt.show()

    centroids = np.array([onaxis_centroid.xyCtr, offaxis_centroid.xyCtr])
    centre = np.array([onaxis.shape[::-1], offaxis.shape[::-1]]) / 2.

    print()

    trans = (centroids[0, :] - centre[0, :]) * pixel_size * focal_scale
    trans[0] *= -1

    print('Translation (Dec, RA): {0}'.format(trans))
    # print('Rotation: {0:.1f}'.format(rot))
    # print('Scale: {0:.3f}'.format(scale))


def show_ds9(image, camera_type, ds9, actor):

    assert camera_type in ['on_axis', 'off_axis']

    try:
        centroid = get_centroid(image.data)
        xx, yy = centroid.xyCtr
    except:
        centroid = None

    if camera_type == 'on_axis':
        frame = 1
    else:
        frame = 2

    ds9.set('frame {0}'.format(frame))
    ds9.set_np2arr(image.data)
    ds9.set('zoom to fit')

    ds9.set('regions command {{point({0}, {1}) # point=cross 20, color=blue}}'.format(
        image.data.shape[1] / 2., image.data.shape[0] / 2.))

    if centroid:
        ds9.set('regions command {{circle({0}, {1}, {2}) # color=green}}'.format(xx, yy,
                                                                                 centroid.rad))
        actor.writeToUsers('d', 'text="{0} camera centroid detected at ({1:.1f}, {2:.1f})"'
                           .format(camera_type, xx, yy))
