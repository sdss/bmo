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

    dirname = os.path.join(actor.config['cameras']['save_path'], str(sjd))
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    files = sorted(glob.glob(os.path.join(dirname, '*.fits*')))

    if len(files) == 0:
        last_no = 0
    else:
        last_no = int(files[-1].split('.')[0].split('-')[-1])

    return dirname, 'bimg-{0:04d}.fits'.format(last_no + 1)


def do_expose(actor, cmd, camera_type, one=False, background=True):
    """Does the actual exposing.

    We keep this function separated because reactor.callLater does not seem to
    work with click.

    """

    if one:
        actor.stop_exposure = True

    camera = actor.cameras[camera_type]
    if camera is None:
        cmd.setState(cmd.Failed, '{0}-axis camera not connected.'.format(camera_type))
        return

    def _process_image(image):
        """Callback to be called when an exposure completes."""

        # If the image is False something went wrong. We reconnect the cameras to
        if image is False:
            actor.writeToUsers('w', 'failed to expose {0} camera. Skipping frame and '
                                    'reconnecting the camera.'.format(camera_type))
            camera.reconnect()
            reactor.callLater(0.1, do_expose, actor, cmd, camera_type, one=False,
                              background=background)
            return

        # Substracts the background.
        # TODO: if the exposure time changes, we should recalculate the background.
        if background is True:
            back_meas = image.subtract_background()
            actor.writeToUsers('d', 'background mean: {0:.3f}'.format(back_meas.background_median))

            # Replaces background with the actual calculated background. We assume that the
            # background does not change that much, so we don't need to calculate it each time.
            background_next = back_meas
        elif background is False:
            background_next = False
        else:
            image.subtract_background(background)
            background_next = background

        # Tries to display the image.
        display_image(image.data, camera_type, actor, cmd)

        camera_ra = camera_dec = -999.

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
            reactor.callLater(0.1, do_expose, actor, cmd, camera_type, one=False,
                              background=background_next)
        else:
            actor.writeToUsers('i', 'text="stopping {0}-axis camera."'.format(camera_type))
            camera.state = 'idle'
            if not cmd.isDone:
                cmd.setState(cmd.Done)

    camera.expose(_process_image)


@click.group()
@click.pass_context
def camera(ctx):
    """Handles the cameras."""
    pass


@camera.command()
@click.option('--camera_type', default='all', type=click.Choice(['all', 'on', 'off']),
              show_default=True,
              help='whether to show all cameras (default) or only on- or off-axis ones.')
@bmo_context
def list(actor, cmd, camera_type):
    """Lists available and connected cameras."""

    actor.writeToUsers('i',
                       'text="Avaliable cameras: {0!r}"'
                       .format(actor.manta_cameras.get_camera_ids()))

    for camera_type in ['on', 'off']:
        camera = actor.cameras[camera_type]
        if camera is None:
            actor.writeToUsers('i', 'text="no {0}-axis camera found"'.format(camera_type))
        else:
            actor.writeToUsers('i', 'text="{0}-axis camera: {1}"'.format(camera_type,
                                                                         camera.camera_id))

    cmd.setState(cmd.Done)

    return False


@camera.command()
@bmo_context
def reconnect(actor, cmd):
    """Forces cameras to reconnect."""

    actor.cameras.connect_all(reconnect=True)
    cmd.setState(cmd.Done)

    return False


@camera.command()
@click.option('--camera_type', default='all', type=click.Choice(['all', 'on', 'off']),
              show_default=True,
              help='whether to expose all connected cameras (default) or only on- or off-axis.')
@click.option('--background/--no-background', default=True, show_default=True,
              help='if True (default), substract a median background from the image.')
@click.option('-o', '--one', is_flag=True, show_default=True,
              help='if set, exposes once with each camera and stops.')
@bmo_context
def expose(actor, cmd, camera_type, background, one=False):
    """Exposes the cameras, showing the result in DS9."""

    camera_types = ['on', 'off'] if camera_type == 'all' else [camera_type]

    actor.stop_exposure = False  # Resets the trigger

    for ct in camera_types:
        actor.cameras[ct].state = 'exposing'
        do_expose(actor, cmd, ct, one=one, background=background)

    return False


@camera.command()
@bmo_context
def stop(actor, cmd):
    """Stops all current exposures."""

    actor.stop_exposure = True
    cmd.setState(cmd.Done)

    return False


@camera.command()
@click.argument('exptime', default=1.0, type=float)
@click.option('--camera_type', default='all', type=click.Choice(['all', 'on', 'off']),
              show_default=True,
              help='whether the exposure time should be set for all cameras (default) '
                   'or only on- or off-axis.')
@bmo_context
def exptime(actor, cmd, exptime, camera_type):
    """Sets the exposure time."""

    camera_types = ['on', 'off'] if camera_type == 'all' else [camera_type]

    for camera_type in camera_types:

        camera = actor.cameras[camera_type]
        if camera is None:
            cmd.setState(cmd.Failed, '{0}-axis camera not connected.'.format(camera_type))
            return

        camera.camera.ExposureTimeAbs = 1e6 * exptime
        actor.writeToUsers('i', 'text="{0}-axis camera set to '
                                'exptime {1:.1f}s."'.format(camera_type, exptime))

    cmd.setState(cmd.Done)

    return False
