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
import re
import sys
import traceback

from twisted.internet import reactor
from twisted.internet.defer import Deferred

from RO.StringUtil import strFromException
from twistedActor import BaseActor, CommandError
from twistedActor.device import ActorDevice, TCPDevice, expandUserCmd

from bmo.cmd.cmd_parser import bmo_parser

from version import __version__


LCOTCC_HOST = 'localhost'
LCOTCC_PORT = 25000


class TCCDevice(TCPDevice):
    """A device to connect to the guider actor."""

    def __init__(self, name, host, port, callFunc=None):

        self.myUserID = None

        self.cmdDone_def = Deferred()

        self._instrumentNum = None

        TCPDevice.__init__(self, name=name, host=host, port=port,
                           callFunc=callFunc, cmdInfo=())

    def update_status(self):
        """Forces the TCC to update some statuses."""

        self._instrumentNum = None
        self.conn.writeLine('999 thread status')

        return

    def init(self, userCmd=None, timeLim=None, getStatus=True):
        """Called automatically on startup after the connection is established.

        Only thing to do is query for status or connect if not connected.

        """

        userCmd = expandUserCmd(userCmd)

        return

    def handleReply(self, replyStr):

        cmdID, userID = map(int, replyStr.split()[0:2])

        if cmdID == 0 and 'yourUserID' in replyStr:
            self.myUserID = int(re.match('.* yourUserID=([0-9]+)(.*)', replyStr).groups()[0])
        elif cmdID != 999 or userID != self.myUserID:
            pass
        elif 'instrumentNum' in replyStr:
            self._instrumentNum = int(re.match('.* instrumentNum=([0-9]+).*',
                                               replyStr).groups()[0])

        self.instrumentNum_def.callback(self._instrumentNum)


class BMOActor(BaseActor):

    def __init__(self, config, **kwargs):
        self.cmdParser = bmo_parser
        self.config = config


        self.cameras = {'on_axis': None,
                        'off_axis': None}
        self.ds9 = None
        self.stop_exposure = False
        self.plate = None

        self.tccActor = TCCDevice('tcc', LCOTCC_HOST, LCOTCC_PORT)
        self.tccActor.connect()

        super(BMOActor, self).__init__(**kwargs)

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

    BMOActor(config, userPort=port, version=__version__)

    reactor.run()
