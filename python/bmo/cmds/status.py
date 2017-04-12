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

    def broadcast_status(status_cmd):
        """Outputs the status of the TCC."""

        if not status_cmd.isDone:
            return

        if status_cmd.didFail:
            cmd.setState(cmd.Failed, 'TCC status command failed. Cannot output status.')
            return

        tcc_status = actor.tccActor.state
        actor.writeToUsers('i', 'text="cartID={0}"'.format(tcc_status.instrumentNum))
        actor.writeToUsers('i', 'text="plate_id={0}"'.format(tcc_status.plate_id))
        actor.writeToUsers('i', 'text="is_ok_to_offset={0}"'.format(tcc_status.is_ok_to_offset()))
        actor.writeToUsers('i', 'text="secOrient={0}"'.format(tcc_status.secOrient))
        actor.writeToUsers('i', 'text="last centroids=({0}, {1})"'
                                .format(actor.state.centroids.on, actor.state.centroids.off))

        if not cmd.isDone:
            cmd.setState(cmd.Done)

        return

    status_cmd = actor.tccActor.update_status()
    status_cmd.addCallback(broadcast_status)

    return False


status_parser = bmo_subparser.add_parser('status', help='returns the status of the actor')
status_parser.set_defaults(func=status)
