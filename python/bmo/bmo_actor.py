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
from twistedActor import BaseActor, CommandError

from cmd.cmd_parser import BMOCmdParser
from cmd.cmd_list import BMO_command_list

from version import __version__


class BMOActor(BaseActor):

    def __init__(self, config, **kwargs):
        self.cmdParser = BMOCmdParser(BMO_command_list)
        super(BMOActor, self).__init__(**kwargs)

    def log_msg(self, msg):
        print('log: {0}'.format(msg))

    def parseAndDispatchCmd(self, cmd):
        """Dispatch the user command."""

        if not cmd.cmdBody:
            # echo to show alive
            self.writeToOneUser(":", "", cmd=cmd)
            return

        try:
            cmd.command, cmd.parsedCmd = self.cmdParser.parse(cmd.cmdBody)
        except Exception as ee:
            cmd.setState(cmd.Failed, 'Could not parse {0:!r}: {1:s}'.format(cmd.cmdBody,
                                                                            strFromException(ee)))
            return

        if cmd.command.call_func:
            cmd.setState(cmd.Running)
            try:
                cmd.command.call_func(self, cmd)
            except CommandError as ee:
                cmd.setState('failed', textMsg=strFromException(ee))
                return
            except Exception as ee:
                sys.stderr.write('command {0:!r} failed\n'.format(cmd.cmdStr,))
                sys.stderr.write('function {0} raised {1}\n'.format(cmd.parsedCmd.callFunc,
                                                                    strFromException(ee)))
                traceback.print_exc(file=sys.stderr)
                textMsg = strFromException(ee)
                hubMsg = 'Exception={0}'.format(ee.__class__.__name__)
                cmd.setState('failed', textMsg=textMsg, hubMsg=hubMsg)
        else:
            raise RuntimeError('Command {0} not yet implemented'.format(cmd.parsedCmd.cmdVerb))


if __name__ == '__main__':

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '../../etc/bmo.cfg'))

    port = config.getint('tron', 'port')
    print('Starting up the actor on port', port)

    BMOActor(config, userPort=port, version=__version__)

    reactor.run()
