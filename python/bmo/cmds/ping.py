#!/usr/bin/env python
# encoding: utf-8
#
# ping.py
#
# Created by José Sánchez-Gallego on 19 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from bmo.cmds.cmd_parser import bmo_subparser


__all__ = ('ping_parser')


def ping(actor, cmd):
    """Pings the actor."""

    cmd.setState(cmd.Done, 'Who wants to play videogames?')

    return False


ping_parser = bmo_subparser.add_parser('ping', help='pings the actor')
ping_parser.set_defaults(func=ping)
