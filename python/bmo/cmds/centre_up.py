#!/usr/bin/env python
# encoding: utf-8
#
# centre_up.py
#
# Created by José Sánchez-Gallego on 19 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import numpy as np

import click
from bmo.cmds import bmo_context

import bmo.utils

__all__ = ('centre_up')


FRAMES = {'on': 1, 'off': 3}


@click.command()
@click.option('-t', '--translate', is_flag=True, help='Only applies translation.')
@click.option('-d', '--dryrun', is_flag=True, help='Calculates offsets but does not apply them.')
@bmo_context
def centre_up(actor, cmd, translate, dryrun):
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

        if on_centroid is None:
            cmd.setState(cmd.Failed, 'Undefined on-axis centroid.')
            return

        if off_centroid is None and translate is False:
            cmd.setState(cmd.Failed, 'Undefined off-axis centroid.')
            return

        ra_offset, dec_offset = bmo.utils.get_translation_offset(on_centroid)

        actor.writeToUsers('w', 'text="translation offset: '
                                '(RA, Dec)=({0:.1f}, {1:.1f})"'.format(ra_offset, dec_offset))

        if off_centroid:
            plate_id = bmo.utils.get_plateid(actor.tccActor.dev_state.instrumentNum)
            rot_offset = bmo.utils.get_rotation_offset(plate_id, off_centroid,
                                                       translation_offset=(ra_offset, dec_offset))
            rot_msg = ' (not applying it)' if translate else ''
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

    if actor.ds9 is None:
        cmd.setState(cmd.Failed, 'no DS9 instance connected.')
        return

    on_centroid = None
    off_centroid = None

    for ct in FRAMES:

        if ct == 'off' and translate is True:
            continue

        try:
            result = bmo.utils.read_ds9_regions(actor.ds9, frame=FRAMES[ct])
        except Exception as ee:
            cmd.setState(cmd.Failed, 'failed retrieving centroids: {0!r}'.format(ee))
            return

        if result[0] is False:
            if actor.centroids[ct] is not None:
                actor.writeToUsers(
                    'w', 'text="cannot read centroid region for {0}-axis camera. '
                         'Using previous value."'.format(ct))
                result = [True, np.array(actor.centroids[ct])]
            else:
                cmd.setState(cmd.Failed, 'failed retrieving centroids: {0!r}'.format(result[1]))
                return

        if ct == 'on':
            on_centroid = result[1][0:2]
        else:
            off_centroid = result[1][0:2]

        actor.writeToUsers('i', 'text="{0}-axis camera: selected centroid at ({1:.1f}, {2:.1f})"'
                           .format(ct, result[1][0], result[1][1]))

    status_cmd = actor.tccActor.update_status()
    if status_cmd is not False:
        status_cmd.addCallback(apply_offsets)
    else:
        cmd.setState(cmd.Failed, 'failed retrieving TCC status. TCC may be dead or disconnected.')
        return

    return False
