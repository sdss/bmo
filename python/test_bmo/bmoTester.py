#!/usr/bin/env python
# encoding: utf-8
#
# bmoTester.py
#
# Created by José Sánchez-Gallego on 4 Jan 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import scipy
import numpy as np


def create_fake_image(n_stars=3, noise=1):

    size_x = 1936
    size_y = 1216

    yy, xx = scipy.mgrid[-size_y / 2:size_y / 2,
                         -size_x / 2:size_x / 2]

    image = np.zeros((size_y, size_x), np.float)

    g_int = 5e5
    positions = []

    for ii in range(n_stars):

        x_star = 2 * (np.random.random() - 0.5) * (size_x - 50) / 2.
        y_star = 2 * (np.random.random() - 0.5) * (size_y - 50) / 2.

        g_size = 1000 * np.random.random()
        g_int *= np.random.random()

        image += g_int * scipy.exp(-((yy - y_star)**2 / g_size + (xx - x_star)**2 / g_size))
        positions.append((size_x / 2 + x_star, size_y / 2 + y_star))

    image_noise = np.random.normal(0., 1e4 * noise, size_x * size_y).reshape((size_y, size_x))
    image += image_noise

    return image, positions
