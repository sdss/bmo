#!/usr/bin/env python
# encoding: utf-8
#
# centre_up.py
#
# Created by José Sánchez-Gallego on 19 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from bmo.cmds.cmd_parser import bmo_subparser
import bmo.utils

__all__ = ('centre_up_parser')


ON_FRAME = 1
OFF_FRAME = 3


def centre_up(actor, cmd):
    """Centres the field."""

    def apply_offsets(status_cmd):

        ra_offset = None
        dec_offset = None
        rot_offset = None

        if not status_cmd.isDone:
            return

        if status_cmd.didFail:
            cmd.setState(cmd.Failed, 'TCC status command failed. Cannot output status.')
            return

        if centroids['on'] is None:
            cmd.setState(cmd.Failed, 'Undefined on-axis centroid.')
            return

        if centroids['off'] is None and only_translation is False:
            cmd.setState(cmd.Failed, 'Undefined off-axis centroid.')
            return

        ra_offset, dec_offset = bmo.utils.get_translation_offset(centroids['on'])

        actor.writeToUsers('w', 'text="translation offset: '
                                '(RA, Dec)=({0:.1f}, {1:.1f})"'.format(ra_offset, dec_offset))

        if centroids['off']:
            plate_id = bmo.utils.get_plateid(actor.tccActor.tcc_state.instrumentNum)
            rot_offset = bmo.utils.get_rotation_offset(plate_id, centroids['off'],
                                                       translation_offset=(ra_offset, dec_offset))
            rot_msg = ' (not applying it)' if only_translation else ''
            actor.writeToUsers('w', 'text="measured rotation '
                                    'offset: {0:.1f}{1}"'.format(rot_offset, rot_msg))
        else:
            actor.writeToUsers('w', 'text="no off-axis centroid. Not calculating rotation."')

        if not dryrun:
            actor.tccActor.offset(ra=ra_offset, dec=dec_offset, rot=rot_offset)
        else:
            actor.writeToUsers('w', 'text="this is a dry-run of centre_up. Not applying offsets."')

        cmd.setState(cmd.Done)

        return

    if actor.state.ds9 is None:
        cmd.setState(cmd.Failed, 'no DS9 instance connected.')
        return

    only_translation = cmd.args.translation
    dryrun = cmd.args.dryrun

    frames_to_get = [ON_FRAME] if only_translation else [ON_FRAME, OFF_FRAME]

    centroids = {'on': None, 'off': None}

    for frame in frames_to_get:

        # If the camera is not running reads the regions because we may have moved them manually.
        # Otherwise it uses the last stored centroids.
        if actor.expose_cmd.isDone:

            try:
                result = bmo.utils.read_ds9_regions(actor.state.ds9, frame=frame)
            except Exception as ee:
                cmd.setState(cmd.Failed, 'failed retrieving centroids: {0!r}'.format(ee))
                return

            if result[0] is False:
                cmd.setState(cmd.Failed, 'failed retrieving centroids: {0!r}'.format(result[1]))
                return

            if frame == ON_FRAME:
                centroids['on'] = result[1][0:2]
            else:
                centroids['off'] = result[1][0:2]

        else:

            centroids['on'] = actor.state.centroids.on
            centroids['off'] = actor.state.centroids.off

        if centroids['on'] is None or centroids['off'] is None:
            cmd.setState(cmd.Failed, 'at least one of the centroids is missing.')
            return

        camera_type = 'on' if frame == ON_FRAME else 'off'
        actor.writeToUsers('i', 'text="{0}-axis camera: selected centroid at ({1:.1f}, {2:.1f})"'
                           .format(camera_type,
                                   centroids[camera_type][0], centroids[camera_type][1]))

    status_cmd = actor.tccActor.update_status()
    status_cmd.addCallback(apply_offsets)

    return False


centre_up_parser = bmo_subparser.add_parser('centre_up', help='centres the field')
centre_up_parser.add_argument('-t', '--translation', action='store_true', default=False,
                              help='only centres up in translation.')
centre_up_parser.add_argument('-d', '--dryrun', action='store_true', default=False,
                              help='calculates offsets but does not apply them.')
centre_up_parser.set_defaults(func=centre_up)
