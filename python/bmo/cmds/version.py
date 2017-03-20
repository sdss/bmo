#!/usr/bin/env python
# encoding: utf-8
#
# version.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from bmo.cmds.cmd_parser import bmo_subparser
from bmo.version import __version__


__all__ = ('version', 'version_parser')


def version(actor, cmd):
    """Returns the version."""

    actor.writeToUsers('i', 'version="{0}"'.format(__version__))
    cmd.setState('done')

    return False


version_parser = bmo_subparser.add_parser('version', help='returns the version of the actor')
version_parser.set_defaults(func=version)
