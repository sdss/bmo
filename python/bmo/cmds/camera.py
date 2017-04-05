#!/usr/bin/env python
# encoding: utf-8
#
# camera.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import time
from twisted.internet import reactor

from astropy.io import fits

from bmo.cmds.cmd_parser import bmo_subparser
from bmo.manta import MantaCamera
from bmo.utils import show_in_ds9

__all__ = ('camera_parser')


def get_list_devices(config):
    """Returns a dictionary of ``'on'`` and ``'off'`` device ids."""

    on_axis = [dev.strip() for dev in config.get('cameras', 'on_axis_devices').split(',')]
    off_axis = [dev.strip() for dev in config.get('cameras', 'off_axis_devices').split(',')]

    return {'on_axis': on_axis, 'off_axis': off_axis}


def get_camera_position(device, config):
    """Returns the position ``'on_axis'`` or ``'off_axis'`` of ``device``.

    Returns ``None`` if the device is not found in the list of valid devices.

    """

    devices = get_list_devices(config)

    if device in devices['on_axis']:
        return 'on_axis'
    elif device in devices['off_axis']:
        return 'off_axis'
    else:
        return None


def camera_list(actor, cmd):
    """Lists available cameras."""

    list_type = cmd.args.list_type

    if list_type == 'available' or list_type == 'all':
        cameras = MantaCamera.list_cameras()
        actor.writeToUsers('i', 'text="Avaliable cameras: {0!r}"'.format(cameras))

    if list_type == 'connected' or list_type == 'all':

        if actor.cameras['on_axis'] is not None:
            actor.writeToUsers(
                'i', 'text="On-axis connected: {0!r}"'.format(actor.cameras['on_axis'].camera_id))
        else:
            actor.writeToUsers('i', 'text="no on-axis connected"')

        if actor.cameras['off_axis'] is not None:
            actor.writeToUsers(
                'i',
                'text="Off-axis connected: {0!r}"'.format(actor.cameras['off_axis'].camera_id))
        else:
            actor.writeToUsers('i', 'text="no off-axis connected"')

    cmd.setState(cmd.Done)

    return False


def camera_connect(actor, cmd):
    """Connects a camera(s)."""

    if cmd.args.camera_type == 'all':
        camera_types = ['on_axis', 'off_axis']
    else:
        camera_types = [cmd.args.camera_type + '_axis']

    available_cameras = {'on_axis': [], 'off_axis': []}
    for dev in MantaCamera.list_cameras():
        dev_position = get_camera_position(dev, actor.config)
        if dev_position is None:
            cmd.setState(cmd.Failed,
                         'device {0!r} is not in the list of valid cameras'.format(dev))
            return
        available_cameras[dev_position].append(dev)

    for camera_type in camera_types:
        str_camera = camera_type.replace('_', '-')
        if len(available_cameras[camera_type]) == 0:
            cmd.setState(cmd.Failed, 'no {0} cameras found'.format(str_camera))
            return
        elif len(available_cameras[camera_type]) > 1:
            cmd.setState(cmd.Failed, 'multiple {0}-axis cameras found'.format(str_camera))
            return

        camera_id = available_cameras[camera_type][0]
        actor.cameras[camera_type] = MantaCamera(camera_id=camera_id)
        actor.writeToUsers('i', 'text="device {0!r} connected as {1} camera"'.format(camera_id,
                                                                                     str_camera),
                           cmd)

    cmd.setState(cmd.Done)

    return False


def camera_expose(actor, cmd):
    """Exposes a camera, showing the result in DS9."""

    # Decides whether we should stop exposing after this iteration.
    actor.stop_exposure = actor.stop_exposure or cmd.args.one

    if cmd.args.camera_type == 'all':
        camera_types = ['on_axis', 'off_axis']
    else:
        camera_types = [cmd.args.camera_type + '_axis']

    for camera_type in camera_types:
        if camera_type not in actor.cameras or actor.cameras[camera_type] is None:
            actor.writeToUsers('w', 'text="{0} camera not connected."'.format(camera_type))
            continue

        camera = actor.cameras[camera_type]
        image = camera.expose()

        actor.writeToUsers('d', 'exposed {0} camera'.format(camera_type))

        try:
            centroid = show_in_ds9(image, camera_type, actor.ds9)
        except Exception as ee:
            cmd.setState(cmd.Failed, 'text="failed to show image in DS9: {0}"'.format(ee))
            return

        if not centroid:
            actor.writeToUsers('i',
                               'text="no centroid detected for {0} camera."'.format(camera_type))
        else:
            xx, yy, __ = centroid
            actor.writeToUsers(
                'i',
                'text="{0} camera centroid detected at ({1:.1f}, {2:.1f})"'.format(camera_type,
                                                                                   xx, yy))

        if cmd.args.save:
            timestr = time.strftime('%d%m%y_%H%M%S')
            fn = '{0}_{1}_{2}.fits'.format(camera.camera_id, camera_type.replace('_', ''), timestr)
            image.save(fn)
            actor.writeToUsers('i', 'saved image {0}'.format(fn))

    if not actor.stop_exposure:
        reactor.callLater(0.1, camera_expose, actor, cmd)
    else:
        actor.writeToUsers('i', 'text="stopping cameras."'.format(camera_type))
        cmd.setState(cmd.Done)

    return False


def camera_stop(actor, cmd):
    """Stops exposures."""

    actor.stop_exposure = True
    cmd.setState(cmd.Done)

    return False


def camera_fake_exposure(actor, cmd):
    """Fakes an exposure."""

    if cmd.args.camera_type == 'all':
        camera_types = ['on_axis', 'off_axis']
    else:
        camera_types = [cmd.args.camera_type + '_axis']

    for camera_type in camera_types:

        if camera_type == 'on_axis':
            fn = 'DEV_000F314D434A_offaxis_180317_194057.fits'
        else:
            fn = 'DEV_000F314D46D2_onaxis_180317_194054.fits'

        full_path = os.path.join(os.path.dirname(__file__), '../', 'data', fn)

        image = fits.open(full_path)[0]
        actor.writeToUsers(
            'i', 'text="displaying image for {0} camera."'.format(camera_type))

        centroid = show_in_ds9(image, camera_type, actor.ds9)
        if not centroid:
            actor.writeToUsers('i',
                               'text="no centroid detected for {0} camera."'.format(camera_type))
        else:
            xx, yy, __ = centroid
            actor.writeToUsers(
                'i',
                'text="{0} camera centroid detected at ({1:.1f}, {2:.1f})"'.format(camera_type,
                                                                                   xx, yy))

    cmd.setState(cmd.Done)

    return False


def camera_exptime(actor, cmd):
    """Set the exposure time."""

    if cmd.args.camera_type == 'all':
        camera_types = ['on_axis', 'off_axis']
    else:
        camera_types = [cmd.args.camera_type + '_axis']

    for camera_type in camera_types:
        if camera_type not in actor.cameras or actor.cameras[camera_type] is None:
            actor.writeToUsers('w', 'text="camera {0} not connected."'.format(camera_type))
            continue

        camera = actor.cameras[camera_type]
        camera.camera.ExposureTimeAbs = 1e6 * cmd.args.exptime
        actor.writeToUsers('i',
                           'text="camera {0} set to exptime {1:.1f}s."'.format(camera_type,
                                                                               cmd.args.exptime))

    cmd.setState(cmd.Done)

    return False


# Here comes the parser  ######################

camera_parser = bmo_subparser.add_parser('camera', help='handles the cameras')
camera_parser_subparser = camera_parser.add_subparsers(title='camera_actions')

# List cameras
camera_parser_list = camera_parser_subparser.add_parser('list', help='lists available cameras')
camera_parser_list.add_argument('list_type', type=str, choices=['available', 'connected', 'all'],
                                default='all', nargs='?')
camera_parser_list.set_defaults(func=camera_list)

# Connect cameras
camera_parser_connect = camera_parser_subparser.add_parser('connect', help='connects a camera')
camera_parser_connect.add_argument('camera_type', type=str, choices=['on', 'off', 'all'],
                                   default='all', nargs='?')
camera_parser_connect.set_defaults(func=camera_connect)

# Expose
camera_parser_expose = camera_parser_subparser.add_parser('expose', help='exposes a camera')
camera_parser_expose.add_argument('camera_type', type=str, choices=['on', 'off', 'all'],
                                  default='all', nargs='?')
camera_parser_expose.add_argument('-s', '--save', action='store_true', default=False)
camera_parser_expose.add_argument('-o', '--one', action='store_true', default=False)
camera_parser_expose.set_defaults(func=camera_expose)

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
