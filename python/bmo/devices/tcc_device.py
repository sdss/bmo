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

from twistedActor.device import TCPDevice, expandUserCmd

from bmo.utils import get_plateid


class TCCStatus(object):

    def __init__(self):

        self.myUserID = None
        self._instrumentNum = None
        self.plate_id = None

        self.axis_states = None

    def reset(self):
        """Resets the status."""

        self.__init__()

    def clear_status(self):
        """Clears status attributes."""

        self._instrumentNum = None
        self.plate_id = None
        self.axis_states = None

    def is_status_complete(self):
        """Returns True if all the status attribute have been set."""

        if self.instrumentNum is not None and self.axis_states is not None:
            return True
        return False

    @property
    def instrumentNum(self):
        return self._instrumentNum

    @instrumentNum.setter
    def instrumentNum(self, value):

        if value > 0:
            self._instrumentNum = value
            self.plate_id = get_plateid(value)
        else:
            self._instrumentNum = None
            self.plate_id = None

    def is_ok_to_offset(self):
        """Returns True if it is ok to offset (all axes are tracking)."""

        if all([xx == 'tracking' for xx in self.axis_states]):
            return True
        else:
            return False


class TCCDevice(TCPDevice):
    """A device to connect to the guider actor."""

    def __init__(self, name, host, port, callFunc=None):

        self.dev_status = TCCStatus()
        self.status_cmd = expandUserCmd(None)

        TCPDevice.__init__(self, name=name, host=host, port=port, callFunc=callFunc, cmdInfo=())

    def update_status(self, cmd=None):
        """Forces the TCC to update some statuses."""

        self.status_cmd = expandUserCmd(cmd)
        self.status_cmd.setTimeLimit(5)

        self.dev_status.clear_status()

        self.conn.writeLine('999 thread status')
        self.conn.writeLine('999 device status tcs')

        self.status_cmd.setState(self.status_cmd.Running)

        return self.status_cmd

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
            self.conn.writeLine('999 guideoffset {0:.6f},{1:.6f},{2:.6f},0.0,0.0'.format(ra, dec,
                                                                                         rot))

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
            pattern = '.* yourUserID=([0-9]+).*'
            self.dev_status.myUserID = int(re.match(pattern, replyStr).group(1))

        # elif cmdID != 999 or userID != self.myUserID:
        #     pass

        elif cmdID == 999 and 'instrumentNum' in replyStr:
            pattern = '.* instrumentNum=([0-9]+).*'
            self.dev_status.instrumentNum = int(re.match(pattern, replyStr).group(1))

        elif 'AxisCmdState' in replyStr:
            axis_states = replyStr.split(';')[7].split('=')[1].split(',')
            self.dev_status.axis_states = [xx.strip().lower() for xx in axis_states]

        if self.dev_status.is_status_complete() and self.status_cmd.isActive:
            self.status_cmd.setState(self.status_cmd.Done, 'TCC status has been updated.')
