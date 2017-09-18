#!/usr/bin/env python
# encoding: utf-8
#
# vimba.py
#
# Created by José Sánchez-Gallego on 17 Sep 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import yaml

from twisted.internet import task

from bmo import config, pathlib
from bmo.logger import log


__all__ = ('Vimba')


class VimbaFrame(object):
    """A fake Vimba frame object."""

    def __init__(self, camera):

        self.camera = camera

    def announceFrame(self):
        """Announces the frame."""

        pass


class VimbaCamera(object):
    """A fake, singleton Vimba camera object."""

    __instances = {}

    def __new__(cls, camera_id, **kwargs):

        if camera_id in VimbaCamera.__instances:
            return VimbaCamera.__instances[camera_id]

        VimbaCamera.__instances[camera_id] = object.__new__(cls)

        return VimbaCamera.__instances[camera_id]

    def openCamera(self):
        """Opens the camera."""

        pass

    def getFrame(self):
        """Returns a frame."""

        return VimbaFrame(self)

    def startCapture(self):
        """Starts camera capture."""

        pass


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

        log.info('[FakeVimba]: starting fake Vimba controller id={}.'
                 .format(id(Vimba.__instance)))

        cls.camera_ids = []

        cls.config_file = pathlib.Path(config['fake_vimba']['config_file']).expanduser()
        cls._file_last_change = 0
        cls.file_watcher_loop = None

        return cls.__instance

    def __init__(self, *args, **kwargs):

        self.process_configuration_file()

        if self.file_watcher_loop is None:
            self.file_watcher_loop = task.LoopingCall(self._file_watcher)
            self.file_watcher_loop.start(config['fake_vimba']['update_interval'])
            log.debug('[FakeVimba]: started watching configuration file {!r} for changes.'
                      .format(str(self.config_file)))

    def startup(self):
        """Starts the controller."""
        pass

    def getSystem(self):
        """Returns an instance of VimbaSystem."""

        return VimbaSystem()

    def getCameraIds(self):
        """Returns a list of connected cameras ids."""

        return self.camera_ids

    def getCamera(self, camera_id):
        """Gets a camera."""

        return VimbaCamera(camera_id)

    def _file_watcher(self):
        """Watches the confiration file for changes."""

        mod_time = self.config_file.stat().st_mtime
        if mod_time > self._file_last_change:
            log.debug('[FakeVimba]: found changes in config file.')
            self.process_configuration_file()

    def process_configuration_file(self):
        """Processes the config file and updates the controller."""

        log.debug('[FakeVimba]: processing configuration file.')
        self._file_last_change = self.config_file.stat().st_mtime

        fake_vimba_config = yaml.load(open(str(self.config_file), 'r'))

        if 'cameras_connected' in fake_vimba_config:
            conn_cameras = fake_vimba_config['cameras_connected']
            assert len(conn_cameras) <= 2, 'too many connected cameras.'

            self.camera_ids = []

            for camera in conn_cameras:
                assert camera in self._valid_devices, 'invalid device {!r}'.format(camera)
                self.camera_ids.append(camera)
