#!/usr/bin/env python
# encoding: utf-8
#
# tcc_device.py
#
# Created by José Sánchez-Gallego on 6 Apr 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re

from twisted.internet import reactor

from twistedActor.device import TCPDevice, expandUserCmd

from bmo.logger import log
from bmo.utils import get_plateid


class TCCState(object):

    def __init__(self):

        self.myUserID = None
        self._instrumentNum = None
        self._plate_id = None
        self._plate_id_previous = None

        self.axis_states = None

        self.secOrient = None

        self.plateid_callback = None

    def reset(self):
        """Resets the status."""

        self.__init__()

    def clear_status(self):
        """Clears status attributes."""

        self.instrumentNum = None
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
            self._instrumentNum = value
            self.plate_id = None

    @property
    def plate_id(self):
        return self._plate_id

    @plate_id.setter
    def plate_id(self, value):

        # Stores previous value
        if self._plate_id is not None:
            self._plate_id_previous = self._plate_id

        self._plate_id = value

        if (self.plate_id is not None and self.plate_id != self._plate_id_previous and
                self.plateid_callback is not None):
            reactor.callLater(0.1, self.plateid_callback, self.plate_id)

    def is_ok_to_offset(self):
        """Returns True if it is ok to offset (all axes are tracking)."""

        if all([xx == 'tracking' for xx in self.axis_states]):
            return True
        else:
            return False


class TCCDevice(TCPDevice):
    """A device to connect to the guider actor."""

    def __init__(self, name, host, port, callFunc=None, actor=None):

        self.dev_state = TCCState()
        self.status_cmd = expandUserCmd(None)
        self.actor = actor

        TCPDevice.__init__(self, name=name, host=host, port=port, callFunc=callFunc, cmdInfo=())

    def update_status(self, cmd=None):
        """Forces the TCC to update some statuses."""

        self.status_cmd = expandUserCmd(cmd)

        log.debug('TCCDevice isDisconnected={!r}, isConnected={!r}, '
                  'isDisconnecting={!r}, state={!r}'.format(self.isDisconnected,
                                                            self.isConnected,
                                                            self.isDisconnecting,
                                                            self.state))

        if self.isDisconnected:
            self.status_cmd.setState(self.status_cmd.Failed, 'TCC is disconnected!')
            return False

        self.status_cmd.setTimeLimit(20)
        self.status_cmd.setState(self.status_cmd.Running)  # must be running to start timer!
        self.dev_state.clear_status()

        self.conn.writeLine('999 device status')

        return self.status_cmd

    def offset(self, user_cmd=None, ra=None, dec=None, rot=None):

        user_cmd = expandUserCmd(user_cmd)

        log.info('{0}.init(user_cmd={1}, ra={2:.6f}, dec={3:.6f}, rot={4:.6f})'
                 .format(self, user_cmd, ra, dec, rot))

        if not self.dev_state.is_ok_to_offset():
            self.writeToUsers('w', 'text="it is not ok to offset!"')
            user_cmd.setState(user_cmd.Failed)
            return

        if ra is None and dec is None and rot is None:
            self.writeToUsers('w', 'text="all offsets are undefined!"')
            user_cmd.setState(user_cmd.Failed)
            return

        self.writeToUsers('w', 'text="boldly going where no man has gone before.""')

        ra = 0.0 if ra is None else ra / 3600.
        dec = 0.0 if dec is None else dec / 3600.
        rot = 0.0 if rot is None else rot / 3600.

        self.conn.writeLine('999 guideoffset {0:.6f},{1:.6f},{2:.6f},0.0,0.0'.format(ra, dec, rot))

        user_cmd.setState(user_cmd.Done, 'hurray!')

        return

    def init(self, userCmd=None, timeLim=None, getStatus=True):
        """Called automatically on startup after the connection is established.

        Only thing to do is query for status or connect if not connected.

        """

        log.info('{0}.init(userCmd={1}, timeLim={2}, getStatus={3})'.format(
            self, userCmd, timeLim, getStatus))

        self.update_status()

        return

    def handleReply(self, replyStr):

        # a less fickle TCC KW listener.
        replyStr = replyStr.strip().lower()  # lower everything to avoide case sensensitivity

        if not replyStr:
            return  # ignore unsolicited response

        cmdID, userID, tccKWs = replyStr.split(None, 2)
        cmdID, userID = int(cmdID), int(userID)

        if cmdID == 0 and 'youruserid' in tccKWs:
            pattern = '.* youruserid=([0-9]+).*'
            self.dev_state.myUserID = int(re.match(pattern, tccKWs).group(1))

        for tccKW in tccKWs.split(';'):

            if 'instrumentnum' in tccKW:
                pattern = '.* instrumentnum=([0-9]+).*'
                instrumentNum = int(re.match(pattern, tccKW).group(1))
                self.dev_state.instrumentNum = instrumentNum

            elif 'axiscmdstate' in tccKW:
                axis_states = tccKW.split('=')[1].split(',')
                axesStates = [xx.strip().lower() for xx in axis_states]
                self.dev_state.axis_states = axesStates

            elif 'secorient' in tccKW:
                secOrient = tccKW.split('=')[-1]
                self.dev_state.secOrient = secOrient

        if self.dev_state.is_status_complete() and not self.status_cmd.isDone:
            self.status_cmd.setState(self.status_cmd.Done, 'TCC status has been updated.')
