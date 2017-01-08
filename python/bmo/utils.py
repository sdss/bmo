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

import matplotlib.pyplot as plt

from bmo import fitData


focal_scale = 3600. / 330.275  # arcsec / mm
pixel_size = 5.86 / 1000.  # in mm


class RotScaleModel(fitData.Model):
    """Model rotation and scale

    out x  =  in x * (c1  -c0)
        y        y   (c0   c1)
            thus:
            rotation = atan2(c0, c1)
            scale = sqrt(c0^2 + c1^2)
    """

    def __init__(self, coeffs=(0.0, 1.0)):
        """Create a model.

        The default coefficients are for no rotation or scale change
        """

        fitData.Model.__init__(self, coeffs)

    def basicApply(self, coeffs, posArr):
        """Compute the fit position given a set of coefficients."""

        # I want rotVec0, rotVec1,... = rotMat * [vec1, vec2,...]
        # but I don't know how to do it, so use this instead
        # rotVec0, rotVec1,... = [vec1, vec2,...] * rotMatTransposed

        rotMatTransposed = np.array(((coeffs[1], coeffs[0]),
                                     (-coeffs[0], coeffs[1])), dtype=float)

        return np.dot(posArr, rotMatTransposed)

    def getInverseCoeffs(self):
        """Get coefficients for inverse transformation."""

        magSq = self._coeffs[0]**2 + self._coeffs[1]**2
        invC2 = -self._coeffs[0] / magSq
        invC3 = self._coeffs[1] / magSq
        return (invC2, invC3)

    def getRotScale(self):
        """Return translation, rotation and scale factor

        Returns:
        - rotation angle, in degrees
        - scale factor

        """

        return (np.arctan2(self._coeffs[0], self._coeffs[1]) / fitData.RadPerDeg,
                np.sqrt(self._coeffs[0]**2 + self._coeffs[1]**2))

    def setTransRotScale(self, rotAng, scale):
        """Set coefficients from translation, rotation and scale factor."""

        rotAngRad = rotAng * fitData.RadPerDeg
        self._coeffs = (scale * np.sin(rotAngRad),
                        scale * np.cos(rotAngRad))


def get_centroid(image):

    mask = np.zeros(image.shape)

    ccdInfo = PyGuide.CCDInfo(np.median(image), 5, 5)
    stars = PyGuide.findStars(image, mask, None, ccdInfo)

    centroids = stars[0]
    assert len(centroids) > 0, 'no centroids found.'

    return centroids[0]


def fit_stars(centroids, nominal):

    fitRotScale = fitData.ModelFit(model=RotScaleModel(coeffs=(0, 1)),
                                   measPos=centroids,
                                   nomPos=nominal,
                                   doRaise=True)

    rotScaleSolution = fitRotScale.model.getRotScale()

    return rotScaleSolution


def calculate_offset(onaxis, offaxis, plot=False):

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
    rot, scale = fit_stars(centroids, centre)

    print()

    trans = (centroids[0, :] - centre[0, :]) * pixel_size * focal_scale
    trans[0] *= -1

    print('Translation (Dec, RA): {0}'.format(trans))
    # print('Rotation: {0:.1f}'.format(rot))
    # print('Scale: {0:.3f}'.format(scale))
