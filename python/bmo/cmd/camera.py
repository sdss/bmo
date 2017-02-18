#!/usr/bin/env python
# encoding: utf-8
#
# camera.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from bmo.cmd.cmd_parser import bmo_subparser
from bmo.manta import MantaCamera

__all__ = ('camera_parser')


def get_list_devices(config):
    """Returns a dictionary of ``'on'`` and ``'off'`` device ids."""

    on_axis = [dev.strip() for dev in config.get('cameras', 'on_axis_devices').split()]
    off_axis = [dev.strip() for dev in config.get('cameras', 'off_axis_devices').split()]

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

    return False


def camera_connect(actor, cmd):

    if cmd.args.camera_type == 'all':
        camera_types = ['on_axis', 'off_axis']
    else:
        camera_types = [cmd.args.camera_type + '_axis']

    available_cameras = {'on_axis': [], 'off_axis': []}
    for dev in MantaCamera.list_cameras():
        dev_position = get_camera_position(dev, actor.config)
        if dev_position is None:
            cmd.setState('failed', 'device {0!r} is not in the list of valid cameras'.format(dev))
            return
        available_cameras[dev_position].append(dev)

    for camera_type in camera_types:
        if len(available_cameras[camera_type]) == 0:
            cmd.setState('failed', 'no {0}-axis cameras found'.format(camera_type))
            return
        elif len(available_cameras[camera_type]) > 1:
            cmd.setState('failed', 'multiple {0}-axis cameras found'.format(camera_type))
            return

        camera_id = available_cameras[camera_type][0]
        actor.cameras[camera_type] = MantaCamera(camera_id=camera_id)
        actor.writeToUsers('i', 'text="device {0!r} connected as {1} camera"'.format(camera_id,
                                                                                     camera_type),
                           cmd)

    return False


camera_parser = bmo_subparser.add_parser('camera', help='handles the cameras')
camera_parser_subparser = camera_parser.add_subparsers(title='camera_actions')

camera_parser_list = camera_parser_subparser.add_parser('list', help='lists available cameras')
camera_parser_list.add_argument('list_type', type=str, choices=['available', 'connected', 'all'],
                                default='all', nargs='?')
camera_parser_list.set_defaults(func=camera_list)

camera_parser_connect = camera_parser_subparser.add_parser('connect', help='connects a camera')
camera_parser_connect.add_argument('camera_type', type=str, choices=['on', 'off', 'all'],
                                   default='all', nargs='?')
camera_parser_connect.set_defaults(func=camera_connect)
