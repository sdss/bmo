#!/usr/bin/env python
# encoding: utf-8
#
# masterThread.py
#
# Created by José Sánchez-Gallego on 15 Oct 2016.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import threading
import Queue

import sdssCamera
from sdssCamera import Msg, myGlobals


def main(actor, queues):
    """Main loop for sdssCamera master thread."""

    threadName = 'master'
    actorState = myGlobals.actorState
    timeout = actorState.timeout

    while True:
        try:
            msg = queues[sdssCamera.MASTER].get(timeout=timeout)

            if msg.type == Msg.EXIT:
                if msg.cmd:
                    msg.cmd.inform('text="Exiting thread {0}"'
                                   .format(threading.current_thread().name))
                return

            elif msg.type == Msg.LIST_THREADS:
                threads = [actorState.threads[pid].name for pid in actorState.threads]
                msg.cmd.inform('text="List of active threads: {0}"'.format(', '.join(threads)))

            else:
                raise ValueError('text="Unknown message type {0}"' .format(msg.type))

        except Queue.Empty:
            actor.bcast.diag('text="{0} alive"'.format(threadName))
        except Exception as ee:
            sdssCamera.handle_bad_exception(actor, ee, threadName, msg)
