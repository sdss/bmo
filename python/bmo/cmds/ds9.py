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
import warnings

from bmo.cmds import bmo_context
from bmo.exceptions import BMOError, BMOUserWarning
from bmo.logger import log
from bmo.utils import get_camera_coordinates, get_acquisition_dss_path

try:
    import pyds9
except ImportError:
    warnings.warn('cannot import pyds9. DS9 features will not work!!', BMOUserWarning)
    pyds9 = None

__all__ = ('ds9')


def prepare_ds9(ds9, only_delete=False):

    ds9.set('frame delete all')

    if only_delete:
        return

    for ii in range(1, 5):
        ds9.set('frame {0}'.format(ii))
        ds9.set('zoom to fit')
        ds9.set('zscale')
        ds9.set('cmap Heat')
        ds9.set('orient none')

    ds9.set('tile mode grid')
    ds9.set('tile grid 2 2')
    ds9.set('tile yes')


def display_dss_from_server(coords, frame, ds9, camera_type, plate_id, width=3, height=3):
    """Displays a DSS image from the internet in a DS9 frame."""

    ds9.set('frame {0}'.format(frame))
    ds9.set('dsseso frame current')
    ds9.set('dsseso size {0} {1}'.format(width, height))
    ds9.set('dsseso coord {0} {1} decimal'.format(coords[0], coords[1]))
    ds9.set('dsseso close')
    ds9.set('wcs append', 'OBJECT = \'{0}axis_{1}\''.format(camera_type, plate_id))

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


def display_dss_from_file(ds9, acq_dss_path, camera_type, plate_id, frame=1):
    """Displays a DSS image from a file."""

    ds9.set('frame {0}'.format(frame))
    ds9.set('fits {0}'.format(acq_dss_path))
    ds9.set('wcs append', 'OBJECT = \'{0}axis_{1}\''.format(camera_type, plate_id))

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


def display_dss(cmd, actor, plate_id, try_server=False):
    """Displays DSS images in DS9.

    It first tries to use the FITS files from platelist. If that fails and
    ``try_server=True``, will try to use the DS9 DSS image server.

    """

    try:

        acq_dss_centre_path = get_acquisition_dss_path(plate_id)
        acq_dss_off_path = get_acquisition_dss_path(plate_id, 'offaxis')

        if acq_dss_centre_path.exists() and acq_dss_off_path.exists():
            display_dss_from_file(actor.ds9, acq_dss_centre_path, 'on', plate_id, frame=2)
            display_dss_from_file(actor.ds9, acq_dss_off_path, 'off', plate_id, frame=4)
            return True

    except (BMOError, AssertionError) as ee:

        log.warning('failed to display DSS images from file: {0}'.format(ee), actor)

    # If try_server=False, returns here and fails.
    if not try_server:
        return False

    # Tries to use DS9 DSS image server

    log.warning('cannot find DSS images for plate {0}. '
                'Using DSS server."'.format(plate_id), actor)

    # Normally, if the images do not exist in platelist, the offaxis coordinates
    # cannot be obtained because they are calculated from the DSS image.
    for camera in ['center', 'offaxis']:

        try:
            coords = get_camera_coordinates(plate_id, camera=camera)
        except (BMOError, AssertionError) as ee:
            log.warning('failed to get {0} camera '
                        'coordinates: {1}"'.format(camera, str(ee)), actor)
            continue

        if not all(coords):
            log.warning('failed to get {0} camera coordinates.'.format(camera), actor)
            continue

        if camera == 'center':
            display_dss_from_server(coords, 2, actor.ds9, 'on', plate_id)
        else:
            display_dss_from_server(coords, 4, actor.ds9, 'off', plate_id)

    return True


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
        address = '{0}:{1}'.format(actor.config['ds9']['host'],
                                   actor.config['ds9']['port'])
        log.debug('using DS9 address from config: {0}'.format(address), actor)

    try:
        actor.ds9 = pyds9.DS9(address)
    except:
        cmd.setState(cmd.Failed, 'cannot connect to {0}'.format(address))
        return

    log.info('connected to DS9 {0}'.format(address), actor)

    prepare_ds9(actor.ds9)

    cmd.setState(cmd.Done)

    return False


@ds9.command()
@click.argument('plate', metavar='PLATE', default=None, type=click.INT, required=False)
@bmo_context
def show_chart(actor, cmd, plate):
    """Shows finding charts for the current plate in DS9."""

    if not actor.ds9:
        cmd.setState(cmd.Failed, 'DS9 is not connected. Try \"bmo ds9 connect\".')
        return

    def show_chart_cb(status_cmd=None):

        if status_cmd is not None and not status_cmd.isDone:
            return

        if status_cmd is not None and status_cmd.didFail:
            cmd.setState(cmd.Failed, 'TCC status command failed. Cannot output status.')
            return

        plate_id = plate or actor.tccActor.dev_state.plate_id
        if plate_id is None:
            cmd.setState(cmd.Failed, 'plate_id is None.')
            return

        result = display_dss(cmd, actor, plate_id)

        if result:
            cmd.setState(cmd.Done, 'DSS finding charts displayed for plate {0}.'.format(plate_id))
        else:
            cmd.setState(cmd.Failed, 'failed finding charts for plate {0}'.format(plate_id))

    if plate is not None:
        show_chart_cb()
        return False

    status_cmd = actor.tccActor.update_status()
    if status_cmd is not False:
        status_cmd.addCallback(show_chart_cb)

    return False


@ds9.command()
@bmo_context
def reset(actor, cmd):
    """Resets the DS9 window."""

    if actor.ds9 is None:
        cmd.setState(cmd.Failed, 'there is no DS9 connection')
        return

    log.info('reseting DS9', actor)
    prepare_ds9(actor.ds9)

    cmd.setState(cmd.Done)

    return False


@ds9.command()
@bmo_context
@click.pass_context
def clear(ctx, actor, cmd):
    """Deletes all DS9 frames. Alias for ``reset``."""

    ctx.invoke(reset)
