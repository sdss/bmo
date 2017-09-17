#!/usr/bin/env python
# encoding: utf-8
#
# status.py
#
# Created by José Sánchez-Gallego on 17 Sep 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from bmo.exceptions import BMOError


__all__ = ('BaseStatus')


class BaseStatus(object):
    """A base clase to represent the status of a device."""

    keywords = []
    _kw_values = {}

    def __init__(self, name):

        self.name = name

    def __getattr__(self, name):
        """Overrides getattr to get keyword values."""

        if name in self.keywords:
            if name in self._kw_values:
                return self._kw_values[name]
            else:
                raise BMOError('cannot find value for keyword {!r}. '
                               'Keyword has not been initialised.'.format(name))

        super(BaseStatus, self).__getattr__(name)

    def __seattr__(self, name, value):
        """Overrides setattr to set keyword values."""

        if name in self.keywords:
            self._kw_values[name] = value

        super(BaseStatus, self).__setattr__(name, value)

    def __dir__(self):
        """Overrides dir to include keywords."""

        return dir(self.__class__) + self.keywords

    def output(self, kw, value=None, user_cmd=None, level='i'):
        """Sets and outputs the value of a keyword."""

        assert level in ['d', 'i', 'w'], 'invalid level.'
        assert kw in self.keywords, 'invalid keyword.'

        if value is not None:
            self._kw_values[kw] = value

        if user_cmd is not None:
            user_cmd.writeToUsers(level, '{0}={1}'.format(kw, self._kw_values[kw]))
