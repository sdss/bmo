#!/usr/bin/env python
# encoding: utf-8
#
# tcc.py
#
# Created by José Sánchez-Gallego on 4 May 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click
from bmo.cmds import bmo_context

try:
    from twistedActor import UserCmd
except ImportError:
    # Doing this so the documentation can build in readthedocs.
    UserCmd = None

__all__ = ('tcc')


@click.command()
@click.argument('command', default='status', type=click.Choice(['status', 'connect', 'disconnect']))
@bmo_context
def tcc(actor, cmd, command):
    """Sends a command to the TCC device.

    In general, only ``bmo tcc connect`` is likely to be used if the connection to the TCC fails.

    """

    if command == 'status':
        cmd_status = UserCmd(cmdStr='status')
        actor.parseAndDispatchCmd(cmd_status)

    elif command == 'connect':
        actor.tccActor.connect()

    elif command == 'disconnect':
        actor.tccActor.disconnect()

    cmd.setState(cmd.Done)

    return False
