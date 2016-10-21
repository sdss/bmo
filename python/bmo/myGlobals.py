#!/usr/bin/env python
# encoding: utf-8
#
# myGlobals.py
#
# Created by José Sánchez-Gallego on 15 Oct 2016.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from sdssCamera.SDSSCameraState import SDSSCameraState

# There are variables that will be populated later on, usually in SDSSCamera,
# and that will be used to share configuration across the whole application.
actorState = None
cameraState = SDSSCameraState()
