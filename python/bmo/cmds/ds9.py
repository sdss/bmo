#!/usr/bin/env python
# encoding: utf-8
#
# ds9.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click
from bmo.cmds import bmo_context

from bmo.utils import get_camera_coordinates

import pyds9

__all__ = ('ds9')


def prepare_ds9(ds9):

    ds9.set('frame delete all')

    for ii in range(1, 5):
        ds9.set('frame {0}'.format(ii))
        ds9.set('zoom to fit')
        ds9.set('zscale')
        ds9.set('cmap Heat')
        ds9.set('orient none')

    ds9.set('tile mode grid')
    ds9.set('tile grid 2 2')
    ds9.set('tile yes')


def display_dss(coords, frame, ds9, width=3, height=3):
    """Displays a DSS image in a DS9 frame."""

    ds9.set('frame {0}'.format(frame))
    ds9.set('dsseso size {0} {1}'.format(width, height))
    ds9.set('dsseso coord {0} {1} decimal'.format(coords[0], coords[1]))
    ds9.set('dsseso close')

    width = ds9.get('fits width')
    centre_w = int(width) / 2

    height = ds9.get('fits height')
    centre_h = int(height) / 2

    ds9.set('regions command {{point({0}, {1}) # point=cross 20, color=blue}}'.format(centre_w,
                                                                                      centre_h))

    ds9.set('zoom to fit')
    ds9.set('minmax')
    ds9.set('orient x')

    return


@click.group()
@click.pass_context
def ds9(ctx):
    """Handles the DS9 communication"""
    pass


@ds9.command()
@click.option('--address', default=None, help='the DS9 intance to which connect.')
@bmo_context
def connect(actor, cmd, address):
    """Connects a DS9 server."""

    if address is None:
        address = '{0}:{1}'.format(actor.config.get('ds9', 'host'),
                                   actor.config.get('ds9', 'port'))
        actor.writeToUsers('d', 'using DS9 address from config: {0}'.format(address))

    try:
        actor.ds9 = pyds9.DS9(address)
    except:
        cmd.setState(cmd.Failed, 'cannot connect to {0}'.format(address))
        return

    actor.writeToUsers('i', 'text="connected to DS9 {0}"'.format(address))
    prepare_ds9(actor.ds9)

    cmd.setState(cmd.Done)

    return False


@ds9.command()
@bmo_context
def show_chart(actor, cmd):
    """Shows finding charts for the current plate in DS9."""

    if not actor.ds9:
        cmd.setState(cmd.Failed, 'DS9 is not connected. Try \"bmo ds9 connect\".')
        return

    def show_chart_cb(status_cmd):

        if not status_cmd.isDone:
            return

        if status_cmd.didFail:
            cmd.setState(cmd.Failed, 'TCC status command failed. Cannot output status.')
            return

        plate_id = actor.tccActor.dev_state.plate_id
        camera_coords = get_camera_coordinates(plate_id)

        display_dss(camera_coords[0], 2, actor.ds9)
        display_dss(camera_coords[1], 4, actor.ds9)

        cmd.setState(cmd.Done, 'DSS finding charts displayed.')

    status_cmd = actor.tccActor.update_status()
    status_cmd.addCallback(show_chart_cb)

    return False


@ds9.command()
@bmo_context
def clear(actor, cmd):
    """Resets the DS9 window."""

    if actor.ds9 is None:
        cmd.setState(cmd.Failed, 'there is no DS9 connection')
        return

    actor.writeToUsers('i', 'text="reseting DS9"')
    prepare_ds9(actor.ds9)

    cmd.setState(cmd.Done)

    return False
