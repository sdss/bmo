#!/usr/bin/env python
# encoding: utf-8
#
# camera.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import glob
import os
from twisted.internet import reactor

import click
from bmo.cmds import bmo_context

from bmo.utils import show_in_ds9, get_sjd, get_camera_coordinates

__all__ = ('camera')


def get_camera_in_position(camera_type, actor):
    """Returns the connected on/off camera, if any."""

    ll = []
    for camera in actor.cameras.cameras:
        if camera.camera_type == camera_type:
            ll.append(camera)

    if len(ll) == 0:
        return None
    elif len(ll) >= 1:
        return ll[0]


def display_image(image, camera_type, actor, cmd):
    """Displays image in DS9 and gets centroids."""

    frame = 1 if camera_type == 'on' else 3

    try:
        centroid = show_in_ds9(image, frame=frame, ds9=actor.ds9)
    except Exception as ee:
        actor.writeToUsers('w', 'text="failed to show image in DS9: {0}"'.format(ee))
        return False

    if not centroid:
        actor.writeToUsers('i', 'text="no centroid detected for '
                                '{0}-axis camera."'.format(camera_type))
    else:
        xx, yy, __ = centroid
        actor.writeToUsers('i', 'text="{0}-axis camera centroid detected '
                                'at ({1:.1f}, {2:.1f})"'.format(camera_type, xx, yy))

    return True


def create_exposure_path(actor):
    """Returns the dirname and basename of the next valid exposure path."""

    sjd = get_sjd()

    dirname = os.path.join(actor.config.get('cameras', 'save_path'), str(sjd))
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    files = sorted(glob.glob(os.path.join(dirname, '*.fits*')))

    if len(files) == 0:
        last_no = 0
    else:
        last_no = int(files[-1].split('.')[0].split('-')[-1])

    return dirname, 'bimg-{0:04d}.fits'.format(last_no + 1)


@click.group()
@click.pass_context
def camera(ctx):
    """Handles the cameras."""
    pass


@camera.command()
@click.argument('camera_type', default='all', type=click.Choice(['all', 'on', 'off']))
@bmo_context
def list(actor, cmd, camera_type):
    """Lists available cameras."""

    actor.writeToUsers('i',
                       'text="Avaliable cameras: {0!r}"'.format(actor.cameras.get_camera_ids()))

    for camera_type in ['on', 'off']:
        camera = get_camera_in_position(camera_type, actor)
        if camera is None:
            actor.writeToUsers('i', 'text="no {0}-axis cameras found"'.format(camera_type))
        else:
            actor.writeToUsers('i', 'text="{0}-axis camera found: {1}"'.format(camera_type,
                                                                               camera.camera_id))

    cmd.setState(cmd.Done)

    return False


@camera.command()
@bmo_context
def reconnect(actor, cmd):
    """Reconnects the cameras."""

    actor.cameras.connect_all(reconnect=True)
    cmd.setState(cmd.Done)

    return False


def do_expose(actor, cmd, camera_type, one=False):
    """Does the actual exposing.

    We keep this function separated because reactor.callLater does not seem to
    work with click.

    """

    camera = get_camera_in_position(camera_type, actor)
    if camera is None:
        cmd.setState(cmd.Failed, '{0}-axis camera not connected.'.format(camera_type))
        return

    image = camera.expose()

    if image is False:
        actor.writeToUsers('w', 'failed to expose {0} camera. Skipping frame and '
                                'reconnecting the camera.'.format(camera_type))
        camera.reconnect()
        reactor.callLater(0.1, do_expose, actor, cmd, camera_type, one=False)
        return

    camera_ra = camera_dec = -999.

    # Tries to display the image.
    display_image(image.data, camera_type, actor, cmd)

    if actor.tccActor.dev_state.plate_id is not None:
        coords = get_camera_coordinates(actor.tccActor.dev_state.plate_id)
        if camera_type == 'on':
            camera_ra = coords[0][0]
            camera_dec = coords[0][1]
        else:
            camera_ra = coords[1][0]
            camera_dec = coords[1][1]

    extra_headers = [('CARTID', actor.tccActor.dev_state.instrumentNum),
                     ('PLATEID', actor.tccActor.dev_state.plate_id),
                     ('CAMTYPE', camera_type + '-axis'),
                     ('SECORIEN', actor.tccActor.dev_state.secOrient)]

    dirname, basename = create_exposure_path(actor)
    fn = image.save(dirname=dirname, basename=basename,
                    camera_ra=camera_ra, camera_dec=camera_dec,
                    extra_headers=extra_headers,
                    compress=False)

    actor.writeToUsers('i', 'text="saved {0}-axis image {1}"'.format(camera_type, fn))

    if not actor.stop_exposure:
        reactor.callLater(0.1, do_expose, actor, cmd, camera_type, one=False)
    else:
        actor.writeToUsers('i', 'text="stopping {0}-axis camera."'.format(camera_type))
        if not cmd.isDone:
            cmd.setState(cmd.Done)


@camera.command()
@click.argument('camera_type', default='all', type=click.Choice(['all', 'on', 'off']))
@click.option('-o', '--one', is_flag=True)
@bmo_context
def expose(actor, cmd, camera_type, one=False):
    """Exposes a camera, showing the result in DS9."""

    camera_types = ['on', 'off'] if camera_type == 'all' else [camera_type]

    # Decides whether we should stop exposing after this iteration.
    actor.stop_exposure = actor.stop_exposure or one

    actor.stop_exposure = False  # Resets the trigger

    for ct in camera_types:
        do_expose(actor, cmd, ct)

    return False


@camera.command()
@bmo_context
def stop(actor, cmd):
    """Stops exposures."""

    actor.stop_exposure = True
    cmd.setState(cmd.Done)

    return False


@camera.command()
@click.argument('exptime', default=1)
@click.option('--camera_type', default='all', type=click.Choice(['all', 'on', 'off']))
@bmo_context
def exptime(actor, cmd, exptime, camera_type):
    """Set the exposure time."""

    camera_types = ['on', 'off'] if camera_type == 'all' else [camera_type]

    for camera_type in camera_types:

        camera = get_camera_in_position(camera_type, actor)
        if camera is None:
            cmd.setState(cmd.Failed, '{0}-axis camera not connected.'.format(camera_type))
            return

        camera.camera.ExposureTimeAbs = 1e6 * exptime
        actor.writeToUsers('i', 'text="{0}-axis camera set to '
                                'exptime {1:.1f}s."'.format(camera_type, exptime))

    cmd.setState(cmd.Done)

    return False
