#!/usr/bin/env python
# encoding: utf-8
#
# bmo_actor.py
#
# Created by José Sánchez-Gallego on 16 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import ConfigParser
import os

from twisted.internet import reactor
from twistedActor import Actor


class BMOActor(Actor):

    def __init__(self, config, **kwargs):
        super(BMOActor, self).__init__(**kwargs)

    def log_msg(self, msg):
        print('log: {0}'.format(msg))


if __name__ == '__main__':

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '../../etc/bmo.cfg'))

    port = config.getint('tron', 'tronCmdrPort')
    print('Starting up the actor on port', port)

    BMOActor(userPort=port)

    reactor.run()
