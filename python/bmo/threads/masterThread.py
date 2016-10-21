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

            elif msg.type == Msg.EXPOSE:
                cState = myGlobals.cameraState
                cState.cameras[msg.camera].expose(exposure_time=msg.exp_time, with_reply=True,
                                                  show=True,
                                                  cmd=msg.cmd,
                                                  reply_queue=queues[sdssCamera.MASTER])

            elif msg.type == Msg.EXPOSURE_DONE:
                if msg.sucess:
                    cState = myGlobals.cameraState
                    import matplotlib.pyplot as plt
                    plt.imshow(cState.cameras['sbig'].last_image.getNumpyArray())
                    plt.show()

                    msg.cmd.inform('text="the exposure is done!"')
                else:
                    msg.cmd.inform('text="the exposure failed!"')

            else:
                raise ValueError('text="Unknown message type {0}"' .format(msg.type))

        except Queue.Empty:
            actor.bcast.diag('text="{0} alive"'.format(threadName))
        except Exception as ee:
            sdssCamera.handle_bad_exception(actor, ee, threadName, msg)
