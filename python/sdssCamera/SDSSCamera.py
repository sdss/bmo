#!/usr/bin/env python
# encoding: utf-8
#
# SDSSCamera.py
#
# Created by José Sánchez-Gallego on 15 Oct 2016.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import abc

import actorcore.Actor

import sdssCamera
from . import SDSSCameraState
from . import masterThread
from . import myGlobals


class SDSSCamera(actorcore.Actor.SDSSActor):
    """Manage the threads that calculate guiding corrections and gcamera commands."""

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def newActor(**kwargs):
        """Return the version of the actor based on our location."""

        return SDSSCameraLCO('camera', productName='sdssCamera', **kwargs)

    def __init__(self, name, debugLevel=30, productName=None, makeCmdrConnection=True):

        actorcore.Actor.Actor.__init__(self, name, productName=productName,
                                       makeCmdrConnection=makeCmdrConnection)

        self.logger.setLevel(debugLevel)
        self.logger.propagate = True

        # Define thread list
        self.threadList = [('master', sdssCamera.MASTER, masterThread)]

        self.models = {}
        self.actorState = actorcore.Actor.ActorState(self, self.models)
        self.actorState.cState = SDSSCameraState.SDSSCameraState()
        self.actorState.actorConfig = self.config
        myGlobals.actorState = self.actorState
        self.actorState.timeout = 60  # timeout on message queues


class SDSSCameraLCO(SDSSCamera):
    """LCO version of this actor."""

    location = 'LCO'
