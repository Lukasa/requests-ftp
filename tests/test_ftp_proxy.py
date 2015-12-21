# -*- encoding: utf-8 -*-

# Requesting an FTP resource through a proxy will actually create a request
# to a HTTP proxy, and the proxy server will handle the FTP parts. This is
# considered OK for some reason.

import pytest

import contextlib
import os
import tempfile
import threading

import requests

from threadmgr import socketServer


@contextlib.contextmanager
def _prepareTestData(dir):
    """ Writes data to the given directory and returns a tuple of (tempname, testdata) """
    with tempfile.NamedTemporaryFile(dir=dir) as f:
        # Write ourself the directory
        with open(__file__, "rb") as testinput:
            testdata = testinput.read()
        f.write(testdata)
        f.flush()

        yield (os.path.basename(f.name), testdata)


def test_proxy_get(ftpd, proxy, session):
    # Create a file in the anonymous root and fetch it through a proxy
    with _prepareTestData(ftpd.anon_root) as (testfile, testdata):
        testurl = 'ftp://127.0.0.1:%d/%s' % (ftpd.ftp_port, testfile)
        response = session.get(testurl, proxies={'ftp': 'localhost:%d' % proxy.port})

        assert response.status_code == requests.codes.ok

        # Check the length
        assert response.headers['Content-Length'] == str(len(testdata))

        # Check the contents
        assert response.content == testdata

        # Check that it went through the proxy
        assert testurl in proxy.requests


def test_proxy_connection_refused(ftpd, session):
    # Create and bind a socket but do not listen to ensure we have a port
    # that will refuse connections
    def target(s, goevent):
        goevent.set()

    with socketServer(target) as port:
        with pytest.raises(requests.exceptions.ConnectionError):
            session.get(
                'ftp://127.0.0.1:%d/' % ftpd.ftp_port,
                proxies={'ftp': 'localhost:%d' % port})


def test_proxy_read_timeout(ftpd, session):
    # Create and accept a socket, but never respond
    def target(s, goevent, event):
        s.listen(1)
        goevent.set()
        (clientsock, _addr) = s.accept()
        try:
            event.wait(5)
        finally:
            clientsock.close()

    event = threading.Event()
    with socketServer(target, event) as port:
        with pytest.raises(requests.exceptions.ReadTimeout):
            session.get(
                'ftp://127.0.0.1:%d' % ftpd.ftp_port,
                proxies={'ftp': 'localhost:%d' % port},
                timeout=1)


def test_proxy_connection_close(ftpd, session):
    # Create and accept a socket, then close it
    def target(s, goevent):
        s.listen(1)
        goevent.set()
        (clientsock, _addr) = s.accept()
        clientsock.close()

    with socketServer(target) as port:
        with pytest.raises(requests.exceptions.ConnectionError):
            session.get(
                'ftp://127.0.0.1:%d/' % ftpd.ftp_port,
                proxies={'ftp': 'localhost:%d' % port},
                timeout=1)
