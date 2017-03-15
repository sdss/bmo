#!/usr/bin/env python
# encoding: utf-8
#
# cmds.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import argparse

__all__ = ('bmo_parser', 'bmo_subparser')


class BMOArgParse(argparse.ArgumentParser):

    def error(self, message):
        raise ValueError(message)


bmo_parser = BMOArgParse(usage=argparse.SUPPRESS)
bmo_subparser = bmo_parser.add_subparsers(title='actions')
