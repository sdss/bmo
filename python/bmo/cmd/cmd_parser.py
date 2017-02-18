#!/usr/bin/env python
# encoding: utf-8
#
# cmds.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from twistedActor.parse import Command, CommandSet


__all__ = ('BMOCommand', 'BMOCmdParser')


class BMOCommand(Command):

    def __init__(self, command_name, **kwargs):
        self.call_func = kwargs.pop('call_func', None)
        super(BMOCommand, self).__init__(command_name, **kwargs)


class BMOCmdParser(CommandSet):

    def __init__(self, command_list):
        super(BMOCmdParser, self).__init__(command_list, actorName='bmo')

    def parse(self, cmdStr):
        """Parse a command string."""

        try:
            cmdName, cmdArgs = cmdStr.split(' ', 1)
        except ValueError:
            # split didn't work (need more than one value to unpack)
            # means that no cmdArgs were passed!
            cmdName = cmdStr
            cmdArgs = ''

        cmdName = cmdName.strip()
        cmdArgs = cmdArgs.strip()
        cmdObj = self.getCommand(cmdName)

        parsed_command = cmdObj.parse(cmdArgs)

        return cmdObj, parsed_command
