#!/usr/bin/env python
# encoding: utf-8
#
# centreup.py
#
# Created by José Sánchez-Gallego on 19 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re

from bmo.cmds.cmd_parser import bmo_subparser

__all__ = ('centre_up_parser')


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

    return True, (xx, yy)


def centre_up(actor, cmd):
    """Centres the field."""

    only_translation = True
    on_orientation = cmd.args.on

    centroids = {}
    for frame in [1, 2]:
        try:
            result = read_ds9_regions(cmd, actor.ds9, frame=frame)
        except Exception as ee:
            cmd.setState(cmd.Failed, 'failed retrieving centroids: {0!r}'.format(ee))
            return

        if result[0] is False:
            cmd.setState(cmd.Failed, 'failed retrieving centroids: {0!r}'.format(ee))
            return

        centroids[frame] = (result[1][0], result[1][1])
        actor.writeToUsers('i', 'text="{0}-axis camera: selected centroid at ({1:.1f}, {2:.1f})"'
                           .format('on' if frame == 1 else 'off',
                                   centroids[frame][0],
                                   centroids[frame][1]))




centre_up_parser = bmo_subparser.add_parser('centre_up', help='centres the field')
centre_up_parser.add_argument('-n', '--on', type=str, default='SE')
centre_up_parser.set_defaults(func=centre_up)
