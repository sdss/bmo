#!/usr/bin/env python
# encoding: utf-8
#
# CameraState.py
#
# Created by José Sánchez-Gallego on 15 Oct 2016.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from sdssCamera.controllers.sbig_camera import SBIG
from sdssCamera.controllers.exceptions import HandlerError, SBIGHandlerError


class SDSSCameraState(object):
    """A class to keep track of the state of SDSS cameras."""

    __valid_cameras__ = ['sbig']

    def __init__(self):

        # Active cameras
        self.cameras = {}

    def init_camera(self, camera):
        """Initialises a camera and its handler and adds it to the list of cameras."""

        camera = camera.lower()

        if camera in self.cameras:
            raise ValueError('camera {0} has already been instantiated.')

        if camera not in self.__valid_cameras__:
            raise ValueError('camera {0} not in list of valid cameras: {1}.'
                             .format(camera, ', '.join(self.__valid_cameras__)))

        if camera == 'sbig':
            self.cameras['sbig'] = SBIG()
            try:
                self.cameras['sbig'].connect()
            except SBIGHandlerError as ee:
                raise HandlerError('problem connecting to SBIG camera: {0}.'.format(ee))
