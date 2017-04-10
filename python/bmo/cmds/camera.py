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

from astropy.io import fits

from bmo.cmds.cmd_parser import bmo_subparser
from bmo.manta import MantaCamera
from bmo.utils import show_in_ds9, get_sjd, get_camera_coordinates

__all__ = ('camera_parser')


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

    files = sorted(glob.glob(os.path.join(dirname, '*.fits')))

    if len(files) == 0:
        last_no = 0
    else:
        last_no = int(files[-1].split('.')[0].split('-')[-1])

    return dirname, 'bimg-{0:04d}.fits'.format(last_no + 1)


def camera_list(actor, cmd):
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


def camera_connect(actor, cmd):
    """Connects a camera(s)."""

    camera_types = ['on', 'off'] if cmd.args.camera_type == 'all' else [cmd.args.camera_type]
    force = cmd.args.force

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


def camera_expose(actor, cmd):
    """Exposes a camera, showing the result in DS9."""

    camera_types = ['on', 'off'] if cmd.args.camera_type == 'all' else [cmd.args.camera_type]

    # Decides whether we should stop exposing after this iteration.
    actor.stop_exposure = actor.stop_exposure or cmd.args.one

    # If camera exposure is called with the --save flag we only take one exposure, and save it.
    if cmd.args.save:
        actor.save_exposure = True
        actor.stop_exposure = True

    for camera_type in camera_types:
        if camera_type not in actor.cameras or actor.cameras[camera_type] is None:
            cmd.setState(cmd.Failed, '{0}-axis camera not connected.'.format(camera_type))
            return

        camera = actor.cameras[camera_type]
        image = camera.expose()

        if image is False:
            actor.writeToUsers('w', 'failed to expose {0} camera. Skipping frame and '
                                    'reconnecting the camera.'.format(camera_type))
            camera.reconnect()
            continue

        camera_ra = camera_dec = -999.

        if actor.tccActor.dev_state.plate_id is not None:
            coords = get_camera_coordinates(actor.tccActor.dev_state.plate_id)
            if camera_type == 'on':
                camera_ra = coords[0]
                camera_dec = coords[1]
            else:
                camera_ra = coords[2]
                camera_dec = coords[3]

        # Tries to display the image.
        display_image(image.data, camera_type, actor, cmd)

        if actor.save_exposure:
            extra_headers = [('CARTID', actor.tccActor.dev_state.instrumentNum),
                             ('PLATEID', actor.tccActor.dev_state.plate_id),
                             ('CAMTYPE', camera_type + '-axis'),
                             ('RACAM', camera_ra),
                             ('DECCAM', camera_dec)]
            dirname, basename = create_exposure_path(actor)
            fn = image.save(dirname=dirname, basename=basename, extra_headers=extra_headers)
            actor.writeToUsers('i', 'saved image {0}'.format(fn))

    actor.save_exposure = False  # Disables saving

    if not actor.stop_exposure:
        reactor.callLater(0.1, camera_expose, actor, cmd)
    else:
        actor.writeToUsers('i', 'text="stopping cameras."'.format(camera_type))
        actor.stop_exposure = False  # Resets the trigger
        cmd.setState(cmd.Done)

    return False


def camera_stop(actor, cmd):
    """Stops exposures."""

    actor.stop_exposure = True
    cmd.setState(cmd.Done)

    return False


def camera_save(actor, cmd):
    """Saves the next exposure(s)."""

    actor.save_exposure = True
    cmd.setState(cmd.Done)

    return False


def camera_fake_exposure(actor, cmd):
    """Fakes an exposure."""

    camera_types = ['on', 'off'] if cmd.args.camera_type == 'all' else [cmd.args.camera_type]

    for camera_type in camera_types:

        if camera_type == 'on':
            fn = 'DEV_000F314D434A_offaxis_180317_194057.fits'
        else:
            fn = 'DEV_000F314D46D2_onaxis_180317_194054.fits'

        full_path = os.path.join(os.path.dirname(__file__), '../', 'data', fn)

        image = fits.open(full_path)[0]

        # Displays the image. Exists if something went wrong.
        if not display_image(image.data, camera_type, actor, cmd):
            return

    cmd.setState(cmd.Done)

    return False


def camera_exptime(actor, cmd):
    """Set the exposure time."""

    camera_types = ['on', 'off'] if cmd.args.camera_type == 'all' else [cmd.args.camera_type]

    for camera_type in camera_types:
        if camera_type not in actor.cameras or actor.cameras[camera_type] is None:
            cmd.setState(cmd.Failed, '{0}-axis camera not connected.'.format(camera_type))
            continue

        camera = actor.cameras[camera_type]
        camera.camera.ExposureTimeAbs = 1e6 * cmd.args.exptime
        actor.writeToUsers('i', 'text="{0}-axis camera set to '
                                'exptime {1:.1f}s."'.format(camera_type, cmd.args.exptime))

    cmd.setState(cmd.Done)

    return False


# Here comes the parser  ######################

camera_parser = bmo_subparser.add_parser('camera', help='handles the cameras')
camera_parser_subparser = camera_parser.add_subparsers(title='camera_actions')

# List cameras
camera_parser_list = camera_parser_subparser.add_parser('list', help='lists available cameras')
camera_parser_list.set_defaults(func=camera_list)

# Connect cameras
camera_parser_connect = camera_parser_subparser.add_parser('connect', help='connects a camera')
camera_parser_connect.add_argument('camera_type', type=str, choices=['on', 'off', 'all'],
                                   default='all', nargs='?')
camera_parser_connect.add_argument('-f', '--force', action='store_true', default=False,
                                   help='forces cameras to reconnect.')
camera_parser_connect.set_defaults(func=camera_connect)

# Expose
camera_parser_expose = camera_parser_subparser.add_parser('expose', help='exposes a camera')
camera_parser_expose.add_argument('camera_type', type=str, choices=['on', 'off', 'all'],
                                  default='all', nargs='?')
camera_parser_expose.add_argument('-s', '--save', action='store_true', default=False)
camera_parser_expose.add_argument('-o', '--one', action='store_true', default=False)
camera_parser_expose.set_defaults(func=camera_expose)

# Save
camera_parser_save = camera_parser_subparser.add_parser('save', help='saves next exposure(s)')
camera_parser_save.set_defaults(func=camera_save)


# Set exposure time
camera_parser_exptime = camera_parser_subparser.add_parser('set_exptime',
                                                           help='sets the exposure time')
camera_parser_exptime.add_argument('camera_type', type=str, choices=['on', 'off', 'all'],
                                   default='all', nargs='?')
camera_parser_exptime.add_argument('exptime', type=float, default=1.)
camera_parser_exptime.set_defaults(func=camera_exptime)

# Fake exposures
camera_parser_fake = camera_parser_subparser.add_parser('fake', help='fakes exposures')
camera_parser_fake.add_argument('camera_type', type=str, choices=['on', 'off', 'all'],
                                default='all', nargs='?')
camera_parser_fake.set_defaults(func=camera_fake_exposure)

# Stop exposing
camera_parser_stop = camera_parser_subparser.add_parser('stop', help='stops exposures')
camera_parser_stop.set_defaults(func=camera_stop)
