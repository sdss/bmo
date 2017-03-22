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
import re

from twisted.internet.defer import Deferred

from bmo.cmds.cmd_parser import bmo_subparser

__all__ = ('centre_up_parser')


FOCAL_SCALE = 3600. / 330.275  # arcsec / mm
PIXEL_SIZE = 5.86 / 1000.  # in mm


def read_ds9_regions(ds9, frame=1):

    ds9.set('frame {0}'.format(frame))
    regions = ds9.get('regions -format ds9 -system image')

    n_circles = regions.count('circle')
    if n_circles == 0:
        return False, 'no circle regions detected in frame {0}'.format(frame)
    elif n_circles > 1:
        return False, 'multiple circle regions detected in frame {0}'.format(frame)

    circle_match = re.match('.*circle\((.*)\)', regions, re.DOTALL)

    if circle_match is None:
        return False, 'cannot parse region in frame {0}'.format(frame)

    try:
        xx, yy = map(float, circle_match.groups()[0].split(',')[0:2])
    except Exception as ee:
        return False, 'problem found while parsing region for frame {0}: {1!r}'.format(frame, ee)

    try:
        height = int(ds9.get('fits height'))
        width = int(ds9.get('fits width'))
    except Exception as ee:
        return False, 'problem found while getting shape for frame {0}: {1!r}'.format(frame, ee)

    return True, (xx, yy, width, height)


def _set_cmd_done(*args):
    cmd = args[-1]
    cmd.setState(cmd.Done)


def centre_up(actor, cmd):
    """Centres the field."""

    if actor.ds9 is None:
        cmd.setState(cmd.Failed, 'no DS9 instance connected.')
        return

    only_translation = True
    on_orientation = cmd.args.on

    frames_to_get = [1, 2]
    if only_translation:
        frames_to_get = [1]

    centroids = {}
    for frame in frames_to_get:
        try:
            result = read_ds9_regions(actor.ds9, frame=frame)
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

    # Solves for translation
    on_centre = np.array([centroids[1][2] / 2., centroids[1][3] / 2.])
    on_centroid = np.array([centroids[1][0], centroids[1][1]])

    trans_ra, trans_dec = (on_centroid - on_centre) * PIXEL_SIZE * FOCAL_SCALE

    if on_orientation == 'WS':
        trans_ra, trans_dec = trans_dec, -trans_ra

    actor.writeToUsers('w', 'translation offset: (RA, Dec)=({0:.1f}, {1:.1f})'.format(trans_ra,
                                                                                      trans_dec))
    actor.tccActor.statusDone_def = Deferred()

    if only_translation:

        actor.tccActor.statusDone_def.addCallbacks(actor.tccActor.offset,
                                                   callbackKeywords={'ra': trans_ra,
                                                                     'dec': trans_dec,
                                                                     'cmd': cmd})
        actor.tccActor.update_status()

        return

    return


centre_up_parser = bmo_subparser.add_parser('centre_up', help='centres the field')
centre_up_parser.add_argument('-n', '--on', type=str, choices=['SE', 'WS'], default='SE',
                              help='the orientation of the on-axis camera, in cardinal '
                                   'points up to right.', nargs='?')
centre_up_parser.set_defaults(func=centre_up)
