# -*- encoding: utf-8 -*-
import contextlib
import six
import socket
import sys
import threading


class TestThread(threading.Thread):
    """ A Thread class that save exceptions raised by the thread. """

    def __init__(self, exnlist, *args, **kwargs):
        self._exnlist = exnlist
        super(TestThread, self).__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        try:
            super(TestThread, self).run(*args, **kwargs)
        except:
            self._exnlist.append(sys.exc_info())


@contextlib.contextmanager
def socketServer(target, event=None):
    """ Starts a server, running target in a new thread.

        Target is the thread target, and will receive the server socket
        and an optional Event as arguments. If event is not None, it
        will be passed as the second argument to target and will be
        set during the __exit__ phase.

        Returns the TCP port the server is running on.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    goevent = threading.Event()

    try:
        s.bind(('', 0))
        port = s.getsockname()[1]

        if event:
            args = (s, goevent, event)
        else:
            args = (s, goevent)

        exn_list = []
        server_thread = TestThread(exn_list, target=target, args=args)
        server_thread.daemon = True
        server_thread.start()

        goevent.wait(5)

        yield port

        if event:
            event.set()

        server_thread.join(1)

        # Check for and re-raise exceptions
        if exn_list:
            exc_info = exn_list[0]
            six.reraise(*exc_info)
    finally:
        s.close()
