#!/usr/bin/env python
# encoding: utf-8
#
# logger.py
#
# Created by José Sánchez-Gallego on 17 Sep 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click
import datetime
import logging
import os
import re
import shutil
import sys
import warnings

from logging.handlers import TimedRotatingFileHandler
from textwrap import TextWrapper

from bmo import config, pathlib


def colored_formatter(record):

    colours = {'info': 'blue',
               'debug': 'magenta',
               'warning': 'yellow'}

    levelname = record.levelname.lower()

    if levelname.lower() in colours:
        levelname_color = colours[levelname]
        header = click.style('[{}]: '.format(levelname.upper()), levelname_color)

    if record.levelno == logging.WARN:
        message = '{0}'.format(record.msg[record.msg.find(':') + 1:])
    else:
        message = '{0}'.format(record.msg)

    # if len(message) > 79:
    #     tw = TextWrapper()
    #     tw.width = 79
    #     tw.subsequent_indent = ' ' * (len(record.levelname) + 2)
    #     tw.break_on_hyphens = False
    #     message = '\n'.join(tw.wrap(message))

    print('{}{}'.format(header, message))

    return


class MyFormatter(logging.Formatter):

    warning_fmp = '%(asctime)s - %(levelname)s: %(message)s [%(origin)s]'
    info_fmt = '%(asctime)s - %(levelname)s - %(message)s [%(funcName)s @ ' + \
        '%(filename)s]'

    ansi_escape = re.compile(r'\x1b[^m]*m')

    def __init__(self, fmt='%(levelname)s - %(message)s [%(funcName)s @ ' +
                 '%(filename)s]'):
        logging.Formatter.__init__(self, fmt, datefmt='%Y-%m-%d %H:%M:%S')

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._fmt = MyFormatter.info_fmt

        elif record.levelno == logging.INFO:
            self._fmt = MyFormatter.info_fmt

        elif record.levelno == logging.ERROR:
            self._fmt = MyFormatter.info_fmt

        elif record.levelno == logging.WARNING:
            self._fmt = MyFormatter.warning_fmp

        record.msg = self.ansi_escape.sub('', record.msg)

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._fmt = format_orig

        return result


Logger = logging.getLoggerClass()
fmt = MyFormatter()


class MyLogger(Logger):
    """This class is used to set up the logging system.

    The main functionality added by this class over the built-in
    logging.Logger class is the ability to keep track of the origin of the
    messages, the ability to enable logging of warnings.warn calls and
    exceptions, and the addition of colorized output and context managers to
    easily capture messages to a file or list.

    """

    def save_log(self, path):
        shutil.copyfile(self.log_filename, os.path.expanduser(path))

    def _showwarning(self, *args, **kwargs):

        warning = args[0]
        message = '{0}: {1}'.format(warning.__class__.__name__, args[0])
        mod_path = args[2]

        mod_name = None
        mod_path, ext = os.path.splitext(mod_path)
        for name, mod in sys.modules.items():
            path = os.path.splitext(getattr(mod, '__file__', ''))[0]
            if path == mod_path:
                mod_name = mod.__name__
                break

        if mod_name is not None:
            self.warning(message, extra={'origin': mod_name})
        else:
            self.warning(message)

    def _set_defaults(self, name,
                      log_level=logging.INFO,
                      log_file_level=logging.DEBUG,
                      log_file_path='~/'):
        """Reset logger to its initial state."""

        # Remove all previous handlers
        for handler in self.handlers[:]:
            self.removeHandler(handler)

        # Set levels
        self.setLevel(logging.DEBUG)

        # Set up the stdout handler
        self.sh = logging.StreamHandler()
        self.sh.emit = colored_formatter
        self.addHandler(self.sh)

        # Set up the main log file handler if requested (but this might fail if
        # configuration directory or log file is not writeable).

        log_file_path = pathlib.Path(log_file_path).expanduser() / '{}.log'.format(name)
        logdir = log_file_path.parent
        logdir.mkdir(parents=True, exist_ok=True)

        # If the log file exists, backs it up before creating a new file handler
        if log_file_path.exists():
            strtime = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S')
            shutil.move(str(log_file_path), str(log_file_path) + '.' + strtime)

        try:
            self.fh = TimedRotatingFileHandler(str(log_file_path), when='midnight', utc=True)
            self.fh.suffix = '%Y-%m-%d_%H:%M:%S'
        except (IOError, OSError) as ee:
            warnings.warn('log file {0!r} could not be opened for writing: '
                          '{1}'.format(log_file_path, ee), RuntimeWarning)
        else:
            self.fh.setFormatter(fmt)
            self.addHandler(self.fh)

        self.sh.setLevel(log_level)
        self.fh.setLevel(log_file_level)

        self.log_filename = log_file_path
        warnings.showwarning = self._showwarning


logging.setLoggerClass(MyLogger)
log = logging.getLogger(__name__)
log._set_defaults('bmo',
                  log_level=logging.INFO,
                  log_file_level=logging.DEBUG,
                  log_file_path=config['logging']['logdir'])
