#!/usr/bin/env python
# encoding: utf-8
#
# ping.py
#
# Created by José Sánchez-Gallego on 19 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click

from bmo.cmds import bmo_context


__all__ = ('ping')


@click.command()
@bmo_context
def ping(actor, cmd):
    """Pings the actor."""

    cmd.setState(cmd.Done, 'Who wants to play videogames?')

    return False
