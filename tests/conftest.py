import pytest
import threading
import requests
import requests_ftp
from simple_ftpd import SimpleFTPServer

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

