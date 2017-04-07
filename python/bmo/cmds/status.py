#!/usr/bin/env python
# encoding: utf-8
#
# status.py
#
# Created by José Sánchez-Gallego on 18 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from bmo.cmds.cmd_parser import bmo_subparser

__all__ = ('status_parser')


def status(actor, cmd):
    """Returns the status."""

    status_cmd = actor.tccActor.update_status()
    status_cmd.setTimeLimit(5)
    status_cmd.addCallback(actor.tccActor.broadcast_status)

    return False


status_parser = bmo_subparser.add_parser('status', help='returns the status of the actor')
status_parser.set_defaults(func=status)
