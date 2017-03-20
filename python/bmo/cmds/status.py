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


def broadcast_tcc(tccActor):
    tccActor.writeToUsers('i', 'text="cartID={0}"'.format(tccActor.instrumentNum))
    tccActor.writeToUsers('i', 'text="ok_to_offset={0}"'.format(tccActor.ok_offset))


def status(actor, cmd):
    """Returns the status."""

    # actor.tccActor.instrumentNum_def.addCallback(broadcast_plate, actor)
    actor.tccActor.update_status(broadcast_tcc)

    return False


status_parser = bmo_subparser.add_parser('status', help='returns the status of the actor')
status_parser.set_defaults(func=status)
