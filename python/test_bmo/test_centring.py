#!/usr/bin/env python
# encoding: utf-8
#
# test_centring.py
#
# Created by José Sánchez-Gallego on 4 Jan 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from unittest import TestCase

from .bmoTester import create_fake_image
from bmo.utils import get_centroid


class TestCentring(TestCase):

    def test_one_image(self):

        image, positions = create_fake_image(n_stars=5)
        centroid = get_centroid(image)[0][0].xyCtr
