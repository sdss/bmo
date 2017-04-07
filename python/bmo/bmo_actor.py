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
import sys
import traceback

from twisted.internet import reactor

from RO.StringUtil import strFromException
from twistedActor import BaseActor, CommandError, UserCmd

from bmo.cmds.cmd_parser import bmo_parser
from bmo.devices.tcc_device import TCCDevice
from version import __version__


LCOTCC_HOST = '10.1.1.20'
LCOTCC_PORT = 25000


class BMOActor(BaseActor):

    def __init__(self, config, autoconnect=True, **kwargs):

        self.cmdParser = bmo_parser
        self.config = config

        self.cameras = {'on_axis': None,
                        'off_axis': None}
        self.ds9 = None
        self.stop_exposure = False

        self.tccActor = TCCDevice('tcc', LCOTCC_HOST, LCOTCC_PORT)
        self.tccActor.writeToUsers = self.writeToUsers
        self.tccActor.connect()

        super(BMOActor, self).__init__(**kwargs)

        if autoconnect is True:
            cmd_ds9 = UserCmd(cmdStr='ds9 connect')
            cmd_camera = UserCmd(cmdStr='camera connect')
            self.parseAndDispatchCmd(cmd_ds9)
            self.parseAndDispatchCmd(cmd_camera)

    def log_msg(self, msg):
        print('log: {0}'.format(msg))

    def parseAndDispatchCmd(self, cmd):
        """Dispatch the user command."""

        if not cmd.cmdBody:
            # echo to show alive
            self.writeToOneUser(":", "", cmd=cmd)
            return

        args = None

        try:

            args = self.cmdParser.parse_args(cmd.cmdBody.split())
            cmd.args = args

            if not hasattr(args, 'func'):
                cmd.setState('failed', textMsg='incomplete command {0!r}'.format(cmd.cmdBody))
                return

        except Exception as ee:

            cmd.setState('failed',
                         textMsg='Could not parse {0!r}: {1}'.format(cmd.cmdBody,
                                                                     strFromException(ee)))
            return

        if not args:
            cmd.setState(cmd.Failed, textMsg='failed to parse command.')
            return

        cmd.setState(cmd.Running)
        try:
            args.func(self, cmd)
        except CommandError as ee:
            cmd.setState('failed', textMsg=strFromException(ee))
            return
        except Exception as ee:
            sys.stderr.write('command {0!r} failed\n'.format(cmd.cmdStr))
            sys.stderr.write('function {0} raised {1}\n'.format(args.func, strFromException(ee)))
            traceback.print_exc(file=sys.stderr)
            textMsg = strFromException(ee)
            hubMsg = 'Exception={0}'.format(ee.__class__.__name__)
            cmd.setState("failed", textMsg=textMsg, hubMsg=hubMsg)


if __name__ == '__main__':

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '../../etc/bmo.cfg'))

    port = config.getint('tron', 'port')
    print('Starting up the actor on port', port)

    BMOActor(config, userPort=port, version=__version__, autoconnect=False)

    reactor.run()
