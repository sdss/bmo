#!/usr/bin/env python
# encoding: utf-8
#
# status.py
#
# Created by José Sánchez-Gallego on 18 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click

from bmo.cmds import bmo_context


__all__ = ('status')


@click.command()
@bmo_context
def status(actor, cmd):
    """Returns the status."""

    from twistedActor import expandCommand

    def broadcast_status(status_cmd):
        """Outputs the status of the TCC."""

        if not status_cmd.isDone:
            return

        if status_cmd.didFail:
            cmd.setState(cmd.Failed, 'TCC status command failed. Cannot output status.')
            return

        tcc_status = actor.tccActor.dev_state
        actor.writeToUsers('i', 'text="cartID={0}"'.format(tcc_status.instrumentNum))
        actor.writeToUsers('i', 'text="plate_id={0}"'.format(tcc_status.plate_id))
        actor.writeToUsers('i', 'text="is_ok_to_offset={0}"'.format(tcc_status.is_ok_to_offset()))
        actor.writeToUsers('i', 'text="secOrient={0}"'.format(tcc_status.secOrient))

        # if not cmd.isDone:
        #     cmd.setState(cmd.Done)

        return

    tcc_status_cmd = expandCommand()
    camera_status_cmd = expandCommand()

    cmd.linkCommands([tcc_status_cmd, camera_status_cmd])

    actor.tccActor.update_status(tcc_status_cmd)
    if tcc_status_cmd is not False:
        tcc_status_cmd.addCallback(broadcast_status)
    else:
        tcc_status_cmd.setState(tcc_status_cmd.Done)

    actor.manta_cameras.update_keywords()

    return False
