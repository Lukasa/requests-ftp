# -*- encoding: utf-8 -*-
import pytest
import requests
import requests_ftp
from simple_ftpd import SimpleFTPServer
from simple_proxy import ProxyServer
import threading


def pytest_configure(config):
    requests_ftp.monkeypatch_session()


@pytest.fixture(scope='session')
def ftpd():
    ftp_server = SimpleFTPServer()
    ftp_server_thread = threading.Thread(target=ftp_server.serve_forever)
    ftp_server_thread.daemon = True
    ftp_server_thread.start()

    return ftp_server


@pytest.fixture
def session():
    return requests.Session()


@pytest.fixture(scope='session')
def proxy():
    proxy_server = ProxyServer()
    proxy_server_thread = threading.Thread(target=proxy_server.serve_forever)
    proxy_server_thread.daemon = True
    proxy_server_thread.start()

    return proxy_server
