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
# import opscore.protocols.types as types

# from opscore.utility.qstr import qstr

import sdssCamera
from sdssCamera import myGlobals, Msg


class CameraCmd(object):

    def __init__(self, actor):

        self.actor = actor

        # Define some typed command arguemetnts
        self.keys = keys.KeysDictionary(
            'camera_camera', (1, 1))

        # Declare commands
        self.vocab = [('listThreads', '', self.listThreads)]

    def listThreads(self, cmd):
        """Print a list of active threads."""

        queue = myGlobals.actorState.queues[sdssCamera.MASTER]
        queue.put(Msg(Msg.LIST_THREADS, cmd=cmd))
