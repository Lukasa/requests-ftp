# -*- encoding: utf-8 -*-
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
        # Write ourself to the directory
        with open(__file__, "rb") as testinput:
            testdata = testinput.read()
        f.write(testdata)
        f.flush()

        yield (os.path.basename(f.name), testdata)


def test_basic_get(ftpd, session):
    # Create a file in the anonymous root and fetch it
    with _prepareTestData(ftpd.anon_root) as (testfile, testdata):
        response = session.get('ftp://127.0.0.1:%d/%s' % (ftpd.ftp_port, testfile))

        assert response.status_code == requests.codes.ok

        # Check the length
        assert response.headers['Content-Length'] == str(len(testdata))

        # Check the contents
        assert response.content == testdata


def test_missing_get(ftpd, session):
    # Fetch a file that does not exist, look for a 404
    response = session.get("ftp://127.0.0.1:%d/no/such/path" % ftpd.ftp_port)
    assert response.status_code == requests.codes.not_found


def test_authenticated_get(ftpd, session):
    # Create a file in the testuser's root and fetch it
    with _prepareTestData(dir=ftpd.ftp_home) as (testfile, testdata):
        response = session.get(
            'ftp://127.0.0.1:%d/%s' % (ftpd.ftp_port, testfile),
            auth=(ftpd.ftp_user, ftpd.ftp_password))

        assert response.status_code == requests.codes.ok
        assert response.headers['Content-Length'] == str(len(testdata))

        # Check the contents
        assert response.content == testdata


def test_head(ftpd, session):
    # Perform a HEAD over an anonymous connection
    with _prepareTestData(dir=ftpd.anon_root) as (testfile, testdata):
        response = session.head('ftp://127.0.0.1:%d/%s' % (ftpd.ftp_port, testfile))

        assert response.status_code == requests.codes.ok
        assert response.headers['Content-Length'] == str(len(testdata))


def test_connection_refused(session):
    # Create and bind a socket but do not listen to ensure we have a port
    # that will refuse connections
    def target(s, goevent):
        goevent.set()

    with socketServer(target) as port:
        with pytest.raises(requests.exceptions.ConnectionError):
            session.get('ftp://127.0.0.1:%d/' % port)


def test_connection_timeout(session):
    # Create, bind, and listen on a socket, but never accept
    def target(s, goevent):
        s.listen(1)
        goevent.set()

    with socketServer(target) as port:
        with pytest.raises(requests.exceptions.ConnectTimeout):
            session.get('ftp://127.0.0.1:%d/' % port, timeout=1)


def test_login_timeout(session):
    # Create and accept a socket, but stop responding after sending
    # the welcome
    def target(s, goevent, event):
        s.listen(1)
        goevent.set()
        (clientsock, _addr) = s.accept()
        try:
            clientsock.send(b'220 welcome\r\n')
            # Wait for the exception to be raised in the client
            event.wait(5)
        finally:
            clientsock.close()

    event = threading.Event()
    with socketServer(target, event) as port:
        with pytest.raises(requests.exceptions.ReadTimeout):
            session.get('ftp://127.0.0.1:%d/' % port, timeout=1)


def test_connection_close(session):
    # Create and accept a socket, then close it after the welcome
    def target(s, goevent):
        s.listen(1)
        goevent.set()
        (clientsock, _addr) = s.accept()
        try:
            clientsock.send(b'220 welcome\r\n')
        finally:
            clientsock.close()

    with socketServer(target) as port:
        with pytest.raises(requests.exceptions.ConnectionError):
            session.get('ftp://127.0.0.1:%d/' % port)


def test_invalid_response(session):
    # Send an invalid welcome
    def target(s, goevent):
        s.listen(1)
        goevent.set()
        (clientsock, _addr) = s.accept()
        try:
            clientsock.send(b'no code\r\n')
        finally:
            clientsock.close()

    with socketServer(target) as port:
        with pytest.raises(requests.exceptions.RequestException):
            session.get('ftp://127.0.0.1:%d/' % port)


def test_invalid_code(session):
    # Send a welcome, then reply with something weird to the USER command
    def target(s, goevent):
        s.listen(1)
        goevent.set()
        (clientsock, _addr) = s.accept()
        try:
            clientsock.send(b'220 welcome\r\n')
            clientsock.recv(1024)
            clientsock.send(b'125 this makes no sense\r\n')
        finally:
            clientsock.close()

    with socketServer(target) as port:
        with pytest.raises(requests.exceptions.RequestException):
            session.get('ftp://127.0.0.1:%d/' % port)


def test_unavailable(session):
    def target(s, goevent):
        s.listen(1)
        goevent.set()
        (clientsock, _addr) = s.accept()
        try:
            clientsock.send(b'421 go away\r\n')
        finally:
            clientsock.close()

    with socketServer(target) as port:
        response = session.get('ftp://127.0.0.1:%d/' % port)
        assert response.status_code == requests.codes.unavailable
