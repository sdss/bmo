#!/usr/bin/env python
# encoding: utf-8
#
# test_centre_up.py
#
# Created by José Sánchez-Gallego on 4 Jan 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
from unittest import TestCase

import astropy.io.fits as fits
import PyGuide

import bmo.utils


class TestOffsets(TestCase):

    @classmethod
    def setUp(cls):

        cls.plate_id = 9459
        cls.on_axis_image = os.path.join(os.path.dirname(__file__),
                                         '../data/DEV_000F314D46D2_onaxis_180317_194054.fits')
        cls.off_axis_image = os.path.join(os.path.dirname(__file__),
                                          '../data/DEV_000F314D434A_offaxis_180317_194057.fits')

        cls.on_axis_centroid = (1752.4199137070332, 454.10706671426425, 29)
        cls.off_axis_centroid = (1743.8137313138916, 422.2838288383008, 247)

    def _check_centroid(self, centroid, expected):

        self.assertAlmostEqual(centroid.xyCtr[0], expected[0])
        self.assertAlmostEqual(centroid.xyCtr[1], expected[1])
        self.assertAlmostEqual(centroid.rad, expected[2])

    def test_get_centroid(self):

        centroid_on_axis = bmo.utils.get_centroid(fits.getdata(self.on_axis_image))
        centroid_off_axis = bmo.utils.get_centroid(fits.getdata(self.off_axis_image))

        self.assertIsInstance(centroid_on_axis, PyGuide.Centroid.CentroidData)
        self.assertIsInstance(centroid_off_axis, PyGuide.Centroid.CentroidData)

        self._check_centroid(centroid_on_axis, self.on_axis_centroid)
        self._check_centroid(centroid_off_axis, self.off_axis_centroid)

    def test_translation(self):

        centroid_on_axis = bmo.utils.get_centroid(fits.getdata(self.on_axis_image))
        shape = (1936, 1216)
        print(centroid_on_axis)
        trans_ra, trans_dec = bmo.utils.get_translation_offset(centroid_on_axis.xyCtr, shape)
        self.assertAlmostEqual(trans_ra, 50.10407236)
        self.assertAlmostEqual(trans_dec, -9.8297640)

    def test_rotation(self):

        centroid_on_axis = bmo.utils.get_centroid(fits.getdata(self.on_axis_image)).xyCtr
        centroid_off_axis = bmo.utils.get_centroid(fits.getdata(self.off_axis_image)).xyCtr

        shape = (1936, 1216)

        trans_ra, trans_dec = bmo.utils.get_translation_offset(centroid_on_axis, shape)

        rotation = bmo.utils.get_rotation_offset(self.plate_id, centroid_off_axis,
                                                 shape=shape,
                                                 translation_offset=(trans_ra, trans_dec))

        self.assertAlmostEqual(rotation, 224.1025775)
