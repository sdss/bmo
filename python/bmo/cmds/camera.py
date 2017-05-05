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

from bmo.manta import MantaCamera, MantaCameraSet
from bmo.utils import show_in_ds9, get_sjd, get_camera_coordinates

__all__ = ('camera')


def get_list_devices(config):
    """Returns a dictionary of ``'on'`` and ``'off'`` device ids."""

    on_axis = [dev.strip() for dev in config.get('cameras', 'on_axis_devices').split(',')]
    off_axis = [dev.strip() for dev in config.get('cameras', 'off_axis_devices').split(',')]

    return {'on': on_axis, 'off': off_axis}


def get_camera_position(device, config):
    """Returns the position ``'on_axis'`` or ``'off_axis'`` of ``device``.

    Returns ``None`` if the device is not found in the list of valid devices.

    """

    devices = get_list_devices(config)

    if device in devices['on']:
        return 'on'
    elif device in devices['off']:
        return 'off'
    else:
        return None


def get_available_cameras(actor, cmd):
    """Returns a list of connected cameras."""

    available_cameras = {'on': [], 'off': []}
    for dev in MantaCamera.list_cameras():
        dev_position = get_camera_position(dev, actor.config)
        if dev_position is None:
            actor.writeToUsers('w', 'device {0!r} is not in the list of known cameras'.format(dev))
        available_cameras[dev_position].append(dev)

    return available_cameras


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

    cameras = MantaCamera.list_cameras()
    actor.writeToUsers('i', 'text="Avaliable cameras: {0!r}"'.format(cameras))

    for camera_type in ['on', 'off']:

        if actor.cameras[camera_type] is not None:
            actor.writeToUsers('i', 'text="{0}-axis connected: '
                                    '{1!r}"'.format(camera_type.capitalize(),
                                                    actor.cameras[camera_type].camera_id))
        else:
            actor.writeToUsers('i', 'text="no {0}-axis connected"'.format(camera_type))

    cmd.setState(cmd.Done)

    return False


@camera.command()
@click.argument('camera_type', default='all', type=click.Choice(['all', 'on', 'off']))
@click.option('--force', is_flag=True)
@bmo_context
def connect(actor, cmd, camera_type, force):
    """Connects a camera(s)."""
    mm = MantaCameraSet()
    camera_types = ['on', 'off'] if camera_type == 'all' else [camera_type]

    available_cameras = get_available_cameras(actor, cmd)

    for camera_type in camera_types:
        if len(available_cameras[camera_type]) == 0:
            cmd.setState(cmd.Failed, 'no {0} cameras found'.format(camera_type))
            return
        elif len(available_cameras[camera_type]) > 1:
            cmd.setState(cmd.Failed, 'multiple {0}-axis cameras found'.format(camera_type))
            return

        camera_id = available_cameras[camera_type][0]

        if (actor.cameras[camera_type] is not None and
                actor.cameras[camera_type].camera.cameraIdString == camera_id):

            if force is False:
                actor.writeToUsers('w', 'text="device {0!r} already connected as {1}-axis camera. '
                                        'Not reconnecting."'.format(camera_id, camera_type))
                continue
            else:
                actor.writeToUsers('w', 'text="device {0!r} already connected as {1}-axis camera. '
                                        'Reconnecting."'.format(camera_id, camera_type))
                actor.cameras[camera_type].close()

        actor.cameras[camera_type] = MantaCamera(camera_id)
        actor.writeToUsers('i', 'text="device {0!r} connected '
                                'as {1} camera"'.format(camera_id, camera_type), cmd)

    cmd.setState(cmd.Done)

    return False


def do_expose(actor, cmd, camera_type, one=False):
    """Does the actual exposing.

    We keep this function separated because reactor.callLater does not seem to
    work with click.

    """

    camera_types = ['on', 'off'] if camera_type == 'all' else [camera_type]

    # Decides whether we should stop exposing after this iteration.
    actor.stop_exposure = actor.stop_exposure or one

    for ct in camera_types:
        if ct not in actor.cameras or actor.cameras[ct] is None:
            cmd.setState(cmd.Failed, '{0}-axis camera not connected.'.format(ct))
            return

        camera = actor.cameras[ct]
        image = camera.expose()

        if image is False:
            actor.writeToUsers('w', 'failed to expose {0} camera. Skipping frame and '
                                    'reconnecting the camera.'.format(ct))
            camera.reconnect()
            continue

        camera_ra = camera_dec = -999.

        # Tries to display the image.
        display_image(image.data, ct, actor, cmd)

        if actor.tccActor.dev_state.plate_id is not None:
            coords = get_camera_coordinates(actor.tccActor.dev_state.plate_id)
            if ct == 'on':
                camera_ra = coords[0][0]
                camera_dec = coords[0][1]
            else:
                camera_ra = coords[1][0]
                camera_dec = coords[1][1]

        extra_headers = [('CARTID', actor.tccActor.dev_state.instrumentNum),
                         ('PLATEID', actor.tccActor.dev_state.plate_id),
                         ('CAMTYPE', ct + '-axis'),
                         ('SECORIEN', actor.tccActor.dev_state.secOrient)]

        dirname, basename = create_exposure_path(actor)
        fn = image.save(dirname=dirname, basename=basename,
                        camera_ra=camera_ra, camera_dec=camera_dec,
                        extra_headers=extra_headers)

        actor.writeToUsers('i', 'saved image {0}'.format(fn))

    if not actor.stop_exposure:
        reactor.callLater(0.1, do_expose, actor, cmd, camera_type, one=False)
    else:
        actor.writeToUsers('i', 'text="stopping cameras."'.format(camera_type))
        actor.stop_exposure = False  # Resets the trigger
        cmd.setState(cmd.Done)


@camera.command()
@click.argument('camera_type', default='all', type=click.Choice(['all', 'on', 'off']))
@click.option('-o', '--one', is_flag=True)
@bmo_context
def expose(actor, cmd, camera_type, one=False):
    """Exposes a camera, showing the result in DS9."""

    do_expose(actor, cmd, camera_type, one=False)

    return False


@camera.command()
@bmo_context
def stop(actor, cmd):
    """Stops exposures."""

    actor.stop_exposure = True
    cmd.setState(cmd.Done)

    return False


@camera.command()
@click.argument('camera_type', default='all', type=click.Choice(['all', 'on', 'off']))
@click.argument('exptime', default=1)
@bmo_context
def exptime(actor, cmd, camera_type, exptime):
    """Set the exposure time."""

    camera_types = ['on', 'off'] if camera_type == 'all' else [camera_type]

    for camera_type in camera_types:
        if camera_type not in actor.cameras or actor.cameras[camera_type] is None:
            cmd.setState(cmd.Failed, '{0}-axis camera not connected.'.format(camera_type))
            continue

        camera = actor.cameras[camera_type]
        camera.camera.ExposureTimeAbs = 1e6 * exptime
        actor.writeToUsers('i', 'text="{0}-axis camera set to '
                                'exptime {1:.1f}s."'.format(camera_type, exptime))

    cmd.setState(cmd.Done)

    return False
