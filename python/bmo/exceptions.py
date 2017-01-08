#!/usr/bin/env python
# encoding: utf-8
#
# exceptions.py
#
# Created by José Sánchez-Gallego on 7 Jan 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


class BMOError(Exception):
    """Base exception for BMO. Other exceptions should inherit this."""


class BMOWarning(Warning):
    """Base warning for BMO."""
    pass


class BMOUserWarning(UserWarning, BMOWarning):
    """The primary warning class."""
    pass
