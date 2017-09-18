#!/usr/bin/env python
# encoding: utf-8
#
# vimba.py
#
# Created by José Sánchez-Gallego on 17 Sep 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


from bmo import config
from bmo.logger import log


__all__ = ('Vimba')


class VimbaSystem(object):
    """A fake, singleton Vimba system object."""

    __instance = None

    __defaults = {'GeVTLIsPresent': True,
                  'camerasIds': []}

    def __new__(cls, *args, **kwargs):

        if VimbaSystem.__instance is not None:
            return VimbaSystem.__instance

        VimbaSystem.__instance = object.__new__(cls)

        # Sets the default values
        for feature, value in cls.__defaults.items():
            setattr(cls, feature, value)

        return VimbaSystem.__instance

    def runFeatureCommand(self, command):
        """Runs a command."""
        pass


class Vimba(object):
    """A fake Vimba controller, mostly for testing purposes."""

    _valid_devices = (config['cameras']['on_axis_devices'] +
                      config['cameras']['off_axis_devices'])

    __instance = None

    def __new__(cls, *args, **kwargs):

        if Vimba.__instance is not None:
            return Vimba.__instance

        Vimba.__instance = object.__new__(cls)

        cls.cameraIds = []

        log.info('starting fake Vimba controller.')

        return Vimba.__instance

    def startup(self):
        """Starts the controller."""
        pass

    def getSystem(self):
        """Returns an instance of VimbaSystem."""

        return VimbaSystem()

    def getCameraIds(self):
        """Returns a list of connected cameras ids."""

        return self.cameraIds
