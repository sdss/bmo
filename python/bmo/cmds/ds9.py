#!/usr/bin/env python
# encoding: utf-8
#
# ds9.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from bmo.cmds.cmd_parser import bmo_subparser
from bmo.utils import get_camera_coordinates

import pyds9

__all__ = ('ds9_parser')


def prepare_ds9(ds9):

    ds9.set('frame delete all')

    for ii in range(1, 5):
        ds9.set('frame {0}'.format(ii))
        ds9.set('zoom to fit')
        ds9.set('zscale')
        ds9.set('cmap Heat')

    ds9.set('tile mode grid')
    ds9.set('tile grid 2 2')
    ds9.set('tile yes')


def ds9_connect(actor, cmd):

    ds9_address = cmd.args.ds9_address
    if ds9_address is None:
        ds9_address = '{0}:{1}'.format(actor.config.get('ds9', 'host'),
                                       actor.config.get('ds9', 'port'))
        actor.writeToUsers('d', 'using DS9 address from config: {0}'.format(ds9_address))

    try:
        actor.ds9 = pyds9.DS9(ds9_address)
    except:
        cmd.setState(cmd.Failed, 'cannot connect to {0}'.format(ds9_address))
        return

    actor.writeToUsers('i', 'text="connected to DS9 {0}"'.format(ds9_address))
    prepare_ds9(actor.ds9)

    cmd.setState(cmd.Done)

    return False


def ds9_show_chart(actor, cmd):
    """Shows finding charts for the current plate in DS9."""

    if not actor.ds9:
        cmd.setState(cmd.Failed, 'DS9 is not connected. Try \"bmo ds9 connect\".')
        return

    def show_chart_cb(status_cmd):

        plate_id = actor.tccActor.dev_state.plate_id
        camera_coords = get_camera_coordinates(plate_id)
        print(camera_coords)

    status_cmd = actor.tccActor.update_status()
    status_cmd.addCallback(show_chart_cb)

    return False


def ds9_clear(actor, cmd):

    if actor.ds9 is None:
        cmd.setState(cmd.Failed, 'there is no DS9 connection')
        return

    actor.writeToUsers('i', 'text="reseting DS9"')
    prepare_ds9(actor.ds9)

    cmd.setState(cmd.Done)

    return False


ds9_parser = bmo_subparser.add_parser('ds9', help='handles the DS9 communication')
ds9_parser_subparser = ds9_parser.add_subparsers(title='ds9_actions')

ds9_parser_connect = ds9_parser_subparser.add_parser('connect', help='connects a DS9 server')
ds9_parser_connect.add_argument('ds9_address', type=str, default=None, nargs='?')
ds9_parser_connect.set_defaults(func=ds9_connect)

ds9_parser_chart = ds9_parser_subparser.add_parser('show_chart',
                                                   help='shows finding charts in DS9')
ds9_parser_chart.set_defaults(func=ds9_show_chart)

ds9_parser_clear = ds9_parser_subparser.add_parser('clear', help='resets the DS9 window')
ds9_parser_clear.set_defaults(func=ds9_clear)
