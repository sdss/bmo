#!/usr/bin/env python
# encoding: utf-8
#
# help.py
#
# Created by José Sánchez-Gallego on 19 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from bmo.cmds.cmd_parser import bmo_subparser


# __all__ = ('help_parser')


def help(actor, cmd):
    """Shows the help."""

    actor.cmdParser.parse_args()
    cmd.setState(cmd.Done)

    return False


# help_parser = bmo_subparser.add_parser('help', help='helps the actor')
# help_parser.set_defaults(func=help)
