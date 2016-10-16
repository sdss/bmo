import actorcore.Actor

from opscore.utility.qstr import qstr
from opscore.utility.tback import tback


# Queue ids
MASTER = 0
GCAMERA = 1
MOVIE = 2


class Msg(actorcore.Actor.Msg):

    # Priorities
    CRITICAL = 0
    HIGH = 2
    MEDIUM = 4
    NORMAL = 6

    class LIST_THREADS(object):
        pass

    class EXIT(object):
        pass

    def __init__(self, typ, cmd, **data):

        self.type = typ
        self.cmd = cmd
        self.priority = Msg.NORMAL  # may be overridden by **data

        for k, v in data.items():
            self.__setattr__(k, v)

        self.__data = data.keys()

    def __repr__(self):
        values = []
        for k in self.__data:
            values.append('%s : %s' % (k, self.__getattribute__(k)))

        return '%s, %s: {%s}' % (self.type.__name__, self.cmd, ', '.join(values))

    def __cmp__(self, rhs):
        """Used when sorting the messages in a priority queue"""
        return self.priority - rhs.priority


def handle_bad_exception(actor, ee, threadName, msg):
    """
    For each thread's "global" unexpected exception handler.
    Send error, dump stacktrace, try to reply with a failure.
    """
    errMsg = qstr('Unexpected exception {0}: {1}, in sop {2} thread'.format(type(ee).__name__,
                                                                            ee, threadName))
    actor.bcast.error('text={0}'.format(errMsg))
    tback(errMsg, ee)
    try:
        msg.replyQueue.put(Msg.REPLY, cmd=msg.cmd, success=False)
    except Exception as ee:
        pass


__all__ = ['MASTER', 'Msg']
