#!/usr/bin/env python
# encoding: utf-8
#
# version.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from .cmd_parser import BMOCommand
from bmo.version import __version__


__all__ = ('version', 'version_cmd')


def version(actor, cmd):
    """Returns the version."""

    actor.writeToUsers('i', 'version="{0}"'.format(__version__))
    cmd.setState('done')

    return False


version_cmd = BMOCommand('version', call_func=version)
