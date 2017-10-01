#!/usr/bin/env python
# encoding: utf-8
#
# help.py
#
# Created by José Sánchez-Gallego on 19 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import json

import click

__all__ = ('help')


@click.command()
@click.pass_context
def help(ctx):
    """Shows the help."""

    cmd = ctx.obj['cmd']

    for line in ctx.parent.get_help().splitlines():
        line = json.dumps(line).replace(';', '')
        cmd.writeToUsers('w', 'text={0}'.format(line))
