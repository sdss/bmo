#!/usr/bin/env python
# encoding: utf-8
#
# cmds.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click

from bmo.cmds.camera import camera
from bmo.cmds.centre_up import centre_up
from bmo.cmds.ds9 import ds9
from bmo.cmds.help import help
from bmo.cmds.ping import ping
from bmo.cmds.status import status
from bmo.cmds.tcc import tcc
from bmo.cmds.version import version


__all__ = ('bmo_parser')


@click.group()
@click.pass_context
def bmo_parser(ctx):
    pass


bmo_parser.add_command(camera)
bmo_parser.add_command(centre_up)
bmo_parser.add_command(ds9)
bmo_parser.add_command(help)
bmo_parser.add_command(ping)
bmo_parser.add_command(status)
bmo_parser.add_command(tcc)
bmo_parser.add_command(version)


if __name__ == '__main__':
    bmo_parser()
