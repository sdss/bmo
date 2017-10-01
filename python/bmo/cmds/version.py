#!/usr/bin/env python
# encoding: utf-8
#
# version.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click
from bmo.cmds import bmo_context

from bmo import __version__


__all__ = ('version')


@click.command()
@bmo_context
def version(actor, cmd):
    """Returns the version."""

    cmd.writeToUsers('i', 'version="{0}"'.format(__version__))
    cmd.setState('done')

    return False
