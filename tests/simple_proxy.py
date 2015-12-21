# -*- encoding: utf-8 -*-
from six.moves import SimpleHTTPServer, socketserver
from six.moves.urllib.request import urlopen


class ProxyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """ Proxy handler that calls a user-provided function and
        forwards the request via urllib.

    """
    def do_GET(self):
        self.server.requests.add(self.path)
        data = urlopen(self.path).read()
        self.send_response(200)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class ProxyServer(socketserver.TCPServer):
    allow_reuse_address = True

    port = property(lambda s: s._port, doc="TCP port the server is running on")

    def __init__(self):
        """ HTTP proxy server

            Can act as a proxy for whatever kinds of URLs urllib can handle.
            Stores requested paths in the set self.requests.

            :param cb: A user-provided method called for each proxy request. The
                       method should take an argument containing the proxied
                       request. The return value will be ignored.
        """

        self.requests = set()

        # Create and bind a new TCPServer on any free port
        socketserver.TCPServer.__init__(self, ('', 0), ProxyHandler)
        self._port = self.socket.getsockname()[1]


if __name__ == "__main__":
    def cb(path):
        print("Proxied request for %s" % path)
    proxy = ProxyServer(cb)
    print("Proxy running on port %d" % proxy.port)
    proxy.serve_forever()
