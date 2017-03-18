#!/usr/bin/env python
# encoding: utf-8
#
# ds9.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from bmo.cmd.cmd_parser import bmo_subparser

import pyds9

__all__ = ('ds9_parser')


def prepare_ds9(ds9):

    ds9.set('frame delete all')
    ds9.set('frame 1')
    ds9.set('zoom to fit')
    ds9.set('frame 2')
    ds9.set('zoom to fit')
    ds9.set('tile mode row')
    ds9.set('tile yes')


def ds9_connect(actor, cmd):

    ds9_address = cmd.args.ds9_address

    try:
        actor.ds9 = pyds9.DS9(ds9_address)
    except:
        cmd.setState('failed', 'cannot connect to {0}'.format(ds9_address))
        return

    actor.writeToUsers('i', 'text="connected to DS9 {0}"'.format(ds9_address))
    prepare_ds9(actor.ds9)


ds9_parser = bmo_subparser.add_parser('ds9', help='handles the DS9 communication')
ds9_parser_subparser = ds9_parser.add_subparsers(title='ds9_actions')

ds9_parser_connect = ds9_parser_subparser.add_parser('connect', help='connects a DS9 server')
ds9_parser_connect.add_argument('ds9_address', type=str)
ds9_parser_connect.set_defaults(func=ds9_connect)
