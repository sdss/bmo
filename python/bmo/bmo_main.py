#!/usr/bin/env python
# encoding: utf-8
#
# bmo_actor.py
#
# Created by José Sánchez-Gallego on 16 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import datetime
import os
import sys
import traceback
import warnings

from click.testing import CliRunner

from twisted.internet import reactor

from RO.StringUtil import strFromException
from twistedActor import BaseActor, CommandError, UserCmd, startFileLogging

from bmo import config
from bmo.cmds.cmd_parser import bmo_parser
from bmo.devices.tcc_device import TCCDevice
from bmo.devices.manta import vimba, MantaCameraSet
from bmo.exceptions import BMOUserWarning

from bmo import __version__


LCOTCC_HOST = '10.1.1.20'
LCOTCC_PORT = 25000


class BMOActor(BaseActor):

    def __init__(self, config, autoconnect=True, **kwargs):

        self.cmdParser = bmo_parser
        self.config = config

        self.ds9 = None
        self.stop_exposure = False
        self.save_exposure = True

        self.cameras = {'on': None, 'off': None}

        self.tccActor = TCCDevice('tcc', LCOTCC_HOST, LCOTCC_PORT)
        self.tccActor.dev_state.plateid_callback = self._plateid_change
        self.tccActor.writeToUsers = self.writeToUsers
        self.tccActor.connect()

        super(BMOActor, self).__init__(**kwargs)

        logPath = self.config['logging']['logdir']
        if not os.path.exists(logPath):
            os.makedirs(logPath)

        rolloverDatetime = datetime.time(hour=13, minute=0, second=0)
        startFileLogging(os.path.join(logPath, 'bmo'), rotate=rolloverDatetime)

        if vimba is not None:
            self.manta_cameras = MantaCameraSet(actor=self)
        else:
            self.manta_cameras = None
            warnings.warn('Vimba is not available. Functionality will be minimal.', BMOUserWarning)

        if autoconnect is True:
            cmd_ds9 = UserCmd(cmdStr='ds9 connect')
            # cmd_camera = UserCmd(cmdStr='camera connect')
            self.parseAndDispatchCmd(cmd_ds9)
            # self.parseAndDispatchCmd(cmd_camera)

    def log_msg(self, msg):
        print('log: {0}'.format(msg))

    def parseAndDispatchCmd(self, cmd):
        """Dispatch the user command."""

        def test_cmd(args):

            result = CliRunner().invoke(bmo_parser, args)
            if result.exit_code > 0:
                # If code > 0, there was an error. We fail the command and inform the users.
                textMsg = result.output
                for line in textMsg.splitlines():
                    self.writeToUsers('w', 'text="{0}"'.format(line))
                cmd.setState(cmd.Failed)
                return False
            else:
                if '--help' in args:
                    # If help was in the args, we just want to print the usage to the users.
                    textMsg = result.output
                    for line in textMsg.splitlines():
                        self.writeToUsers('w', 'text="{0}"'.format(line))
                    cmd.setState(cmd.Done)
                    return False

                return True

        if not cmd.cmdBody:
            # echo to show alive
            self.writeToOneUser(":", "", cmd=cmd)
            return

        cmd.setState(cmd.Running)

        try:
            result = test_cmd(cmd.cmdBody.split())
            if result is False:
                return
            bmo_parser(cmd.cmdBody.split(), obj=dict(actor=self, cmd=cmd))
        except CommandError as ee:
            cmd.setState('failed', textMsg=strFromException(ee))
            return
        except Exception as ee:
            sys.stderr.write('command {0!r} failed\n'.format(cmd.cmdStr))
            # sys.stderr.write('function {0} raised {1}\n'.format(args.func, strFromException(ee)))
            traceback.print_exc(file=sys.stderr)
            textMsg = strFromException(ee)
            hubMsg = 'Exception={0}'.format(ee.__class__.__name__)
            cmd.setState("failed", textMsg=textMsg, hubMsg=hubMsg)
        except BaseException:
            # This catches the SystemExit that Click insists in returning.
            pass

    def _plateid_change(self, plate_id):
        """Callback to be executed if the instrumentNum changes."""

        if plate_id is None:
            return

        cmd_chart = UserCmd(cmdStr='ds9 show_chart --plate {0}'.format(plate_id))
        self.parseAndDispatchCmd(cmd_chart)


if __name__ == '__main__':

    port = config['tron']['port']
    print('Starting up the actor on port', port)

    BMOActor(config, userPort=port, version=__version__, autoconnect=True)

    reactor.run()
