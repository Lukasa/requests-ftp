# -*- encoding: utf-8 -*-
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

import shutil
import socket
import tempfile


class SimpleFTPServer(FTPServer):
    """Starts a simple FTP server on a random free port. """

    ftp_user = property(
        lambda s: 'fakeusername',
        doc='User name added for authenticated connections')
    ftp_password = property(lambda s: 'qweqwe', doc='Password for ftp_user')

    # Set in __init__
    anon_root = property(lambda s: s._anon_root, doc='Home directory for the anonymous user')
    ftp_home = property(lambda s: s._ftp_home, doc='Home directory for ftp_user')
    ftp_port = property(lambda s: s._ftp_port, doc='TCP port that the server is listening on')

    def __init__(self):
        # Create temp directories for the anonymous and authenticated roots
        self._anon_root = tempfile.mkdtemp()
        self._ftp_home = tempfile.mkdtemp()

        authorizer = DummyAuthorizer()
        authorizer.add_user(self.ftp_user, self.ftp_password, self.ftp_home, perm='elradfmwM')
        authorizer.add_anonymous(self.anon_root)

        handler = FTPHandler
        handler.authorizer = authorizer

        # Create a socket on any free port
        self._ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ftp_socket.bind(('', 0))
        self._ftp_port = self._ftp_socket.getsockname()[1]

        # Create a new pyftpdlib server with the socket and handler we've configured
        FTPServer.__init__(self, self._ftp_socket, handler)

    def __del__(self):
        self.close_all()

        if hasattr(self, '_anon_root'):
            shutil.rmtree(self._anon_root, ignore_errors=True)

        if hasattr(self, '_ftp_home'):
            shutil.rmtree(self._ftp_home, ignore_errors=True)

if __name__ == "__main__":
    server = SimpleFTPServer()
    print("FTPD running on port %d" % server.ftp_port)
    print("Anonymous root: %s" % server.anon_root)
    print("Authenticated root: %s" % server.ftp_home)
    server.serve_forever()
