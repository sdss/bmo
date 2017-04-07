#!/usr/bin/env python
# encoding: utf-8
#
# file.py
#
# Created by José Sánchez-Gallego on 6 Apr 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re

from twistedActor.command import expandUserCmd
from twistedActor.device import TCPDevice, expandUserCmd

from bmo.utils import get_plateid


class TCCStatus(object):

    def __init__(self):

        self.myUserID = None
        self.instrumentNum = None
        self.plate_id = None

        self.axis_states = None

    def reset(self):
        """Resets the status."""

        self.__init__()

    def clear_status(self):
        """Clears status attributes."""

        self.instrumentNum = None
        self.plate_id = None
        self.axis_states = None

    def is_ok_to_offset(self):
        """Returns True if it is ok to offset (all axes are tracking)."""

        if all([xx.strip().lower() == 'tracking' for xx in self.axis_states]):
            return True
        else:
            return False


class TCCDevice(TCPDevice):
    """A device to connect to the guider actor."""

    def __init__(self, name, host, port, callFunc=None):

        self.status = TCCStatus()
        self.status_cmd = None

        TCPDevice.__init__(self, name=name, host=host, port=port,
                           callFunc=callFunc, cmdInfo=())

    def update_status(self, cmd=None):
        """Forces the TCC to update some statuses."""

        self.instrumentNum = None
        self.ok_offset = None
        self.conn.writeLine('999 thread status')
        self.conn.writeLine('999 device status tcs')

        return

    def offset(self, *args, **kwargs):

        cmd = kwargs.get('cmd', None)

        if not self.ok_offset:
            if cmd:
                cmd.setState(cmd.Failed, 'it is not ok to offset!')
            return

        self.writeToUsers('w', 'boldly going where no man has gone before.')

        ra = kwargs['ra'] / 3600.
        dec = kwargs['dec'] / 3600.

        if 'rot' not in kwargs:
            self.conn.writeLine('999 offset arc {0:.6f},{1:.6f}'.format(ra, dec))
        else:
            rot = -kwargs['rot'] / 3600.
            self.conn.write('999 guideoffset {0:.6f},{1:.6f},{2:.6f},0.0,0.0'.format(ra, dec, rot))

        if cmd:
            cmd.setState(cmd.Done, 'hurray!')

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
