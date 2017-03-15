#!/usr/bin/env python
# encoding: utf-8
#
# test_plot.py
#
# Created by José Sánchez-Gallego on 7 Jan 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from bmoTester import create_fake_image
from bmo.utils import calculate_offset


img1 = create_fake_image(n_stars=3)[0]
img2 = create_fake_image(n_stars=2)[0]

calculate_offset(img1, img2, plot=True)
