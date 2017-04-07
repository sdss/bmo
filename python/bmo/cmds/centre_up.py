#!/usr/bin/env python
# encoding: utf-8
#
# centre_up.py
#
# Created by José Sánchez-Gallego on 19 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from twisted.internet.defer import Deferred

from bmo.cmds.cmd_parser import bmo_subparser
import bmo.utils

__all__ = ('centre_up_parser')


def _set_cmd_done(*args):
    cmd = args[-1]
    cmd.setState(cmd.Done)


def _apply_offset(*args, **kwargs):

    actor = kwargs['actor']

    plate_id = bmo.utils.get_plateid(kwargs['actor'].tccActor.instrumentNum)
    rotation = bmo.utils.get_rotation_offset(plate_id, kwargs['off_centroid'])
    kwargs['rot'] = rotation

    actor.writeToUsers('w', 'rotation offset: {0:.1f}'.format(rotation))
    actor.tccActor.offset(**kwargs)


def centre_up(actor, cmd):
    """Centres the field."""

    if actor.ds9 is None:
        cmd.setState(cmd.Failed, 'no DS9 instance connected.')
        return

    only_translation = cmd.args.translation
    on_orientation = cmd.args.on

    frames_to_get = [1, 2]
    if only_translation:
        frames_to_get = [1]

    centroids = {}
    for frame in frames_to_get:
        try:
            result = bmo.utils.read_ds9_regions(actor.ds9, frame=frame)
        except Exception as ee:
            cmd.setState(cmd.Failed, 'failed retrieving centroids: {0!r}'.format(ee))
            return

        if result[0] is False:
            cmd.setState(cmd.Failed, 'failed retrieving centroids: {0!r}'.format(result[1]))
            return

        centroids[frame] = result[1]
        actor.writeToUsers('i', 'text="{0}-axis camera: selected centroid at ({1:.1f}, {2:.1f})"'
                           .format('on' if frame == 1 else 'off',
                                   centroids[frame][0],
                                   centroids[frame][1]))

    on_axis_centroid = centroids[1][0:2]
    on_axis_shape = centroids[1][2:]
    trans_ra, trans_dec = bmo.utils.get_translation_offset(on_axis_centroid, on_axis_shape,
                                                           orientation=on_orientation)

    actor.writeToUsers('w', 'translation offset: (RA, Dec)=({0:.1f}, {1:.1f})'.format(trans_ra,
                                                                                      trans_dec))
    actor.tccActor.statusDone_def = Deferred()

    if only_translation:

        actor.tccActor.statusDone_def.addCallbacks(actor.tccActor.offset,
                                                   callbackKeywords={'ra': trans_ra,
                                                                     'dec': trans_dec,
                                                                     'cmd': cmd})
        actor.tccActor.update_status()

        return False

    # Calculates rotation

    off_axis_centroid = centroids[2][0:2]
    actor.tccActor.statusDone_def.addCallbacks(_apply_offset,
                                               callbackKeywords={'ra': trans_ra,
                                                                 'dec': trans_dec,
                                                                 'actor': actor,
                                                                 'off_centroid': off_axis_centroid,
                                                                 'cmd': cmd})
    actor.tccActor.update_status()

    return False


centre_up_parser = bmo_subparser.add_parser('centre_up', help='centres the field')
centre_up_parser.add_argument('-t', '--translation', action='store_true', default=False,
                              help='only centres up in translation.')
centre_up_parser.add_argument('-n', '--on', type=str, choices=['SE', 'WS'], default='SE',
                              help='the orientation of the on-axis camera, in cardinal '
                                   'points up to right.', nargs='?')
centre_up_parser.set_defaults(func=centre_up)
