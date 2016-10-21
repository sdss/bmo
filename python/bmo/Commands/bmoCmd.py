#!/usr/bin/env python
# encoding: utf-8
#
# CameraCmd.py
#
# Created by José Sánchez-Gallego on 15 Oct 2016.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import opscore.protocols.keys as keys
import opscore.protocols.types as types

from opscore.utility.qstr import qstr

import sdssCamera
from sdssCamera import myGlobals, Msg
from sdssCamera.controllers.exceptions import HandlerError


class CameraCmd(object):

    def __init__(self, actor):

        self.actor = actor

        # Define some typed command arguemetnts
        self.keys = keys.KeysDictionary(
            'camera_camera', (1, 1),
            keys.Key('camera', types.String(), help='The camera to initialise.'),
            keys.Key('exptime', types.Float(), help='Exposure time.'))

        # Declare commands
        self.vocab = [
            ('listThreads', '', self.list_threads),
            ('init', '(sbig|manta)', self.init_camera),
            ('expose', '<camera> <exptime>', self.expose)]

    def list_threads(self, cmd):
        """Print a list of active threads."""

        queue = myGlobals.actorState.queues[sdssCamera.MASTER]
        queue.put(Msg(Msg.LIST_THREADS, cmd=cmd))

    def init_camera(self, cmd):
        """Initialises a camera with its handler."""

        camera = cmd.cmd.keywords[0].name.lower()

        try:
            cState = myGlobals.cameraState
            cState.init_camera(camera)
        except (ValueError, HandlerError) as ee:
            cmd.fail('text="{0}"'.format(qstr(ee)))

        cmd.inform('text="successfully connected to {0}"'.format(camera))

        return

    def expose(self, cmd):
        """Takes and exposure."""

        camera_name = cmd.cmd.keywords['camera'].values[0]
        exp_time = cmd.cmd.keywords['exptime'].values[0]

        queue = myGlobals.actorState.queues[sdssCamera.MASTER]
        queue.put(Msg(Msg.EXPOSE, cmd=cmd, camera=camera_name, exp_time=exp_time))
