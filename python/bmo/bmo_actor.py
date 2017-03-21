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
from twistedActor.device import TCPDevice, expandUserCmd

from bmo.cmds.cmd_parser import bmo_parser
from bmo.utils import get_plateid

from version import __version__


LCOTCC_HOST = '10.1.1.20'
LCOTCC_PORT = 25000


class TCCStatus(object):

    def __init__(self):

        self.myUserID = None
        self.statusDone_def = Deferred()
        self.instrumentNum = None
        self.plate_id = None
        self.ok_offset = None

    def reset(self):
        self.__init__()


class TCCDevice(TCPDevice):
    """A device to connect to the guider actor."""

    def __init__(self, name, host, port, callFunc=None):

        self.myUserID = None
        self.statusDone_def = Deferred()
        self.instrumentNum = None
        self.plate_id = None
        self.ok_offset = None

        TCPDevice.__init__(self, name=name, host=host, port=port,
                           callFunc=callFunc, cmdInfo=())

    def update_status(self):
        """Forces the TCC to update some statuses."""

        self.instrumentNum = None
        self.ok_offset = None
        self.conn.writeLine('999 thread status')
        self.conn.writeLine('999 device status tcs')

        return

    def offset(self, *args, **kwargs):

        cmd = kwargs['cmd']

        if not self.ok_offset:
            cmd.setState(cmd.Failed, 'it is not ok to offset!')
            return

        self.writeToUsers('w', 'boldly going where no man has gone before.')
        self.conn.writeLine('999 offset arc {0:.6f},{1:.6f}'.format(kwargs['ra'] / 3600.,
                                                                    kwargs['dec'] / 3600.))

        cmd.setState(cmd.Done, 'hurray!')

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

        # elif cmdID != 999 or userID != self.myUserID:
        #     pass

        elif cmdID == 999 and 'instrumentNum' in replyStr:
            self.instrumentNum = int(re.match('.* instrumentNum=([0-9]+).*', replyStr).groups()[0])
            if self.instrumentNum is not None and self.instrumentNum > 0:
                try:
                    self.plate_id = get_plateid(self.instrumentNum)
                except:
                    self.writeToUsers(
                        'w', 'failed to get plate_id for cart {0}'.format(self.instrumentNum))

        elif 'AxisCmdState' in replyStr:
            axis_states = replyStr.split(';')[7].split('=')[1].split(',')
            if all([xx.strip().lower() == 'tracking' for xx in axis_states]):
                self.ok_offset = True
            else:
                self.ok_offset = False

        if self.ok_offset is not None and self.instrumentNum is not None:
            if not self.statusDone_def.called:
                self.statusDone_def.callback(self)


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
        self.tccActor.writeToUsers = self.writeToUsers
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
