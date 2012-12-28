# -*- encoding: utf-8 -*-
from requests.adapters import BaseAdapter
import ftplib
import base64
from requests.compat import urlparse, StringIO
from requests.hooks import dispatch_hook
from requests import Response


def data_callback_factory(variable):
    '''Returns a callback suitable for use by the FTP library. This callback
    will repeatedly save data into the variable provided to this function. This
    variable should be a file-like structure.'''
    def callback(data):
        variable.write(data)
        return

    return callback


def build_text_response(request, data):
    '''Build a response for textual data.'''
    return build_response(request, data, 'ascii')


def build_binary_response(request, data):
    '''Build a response for data whose encoding is unknown.'''
    return build_response(request, data, None)


def build_response(request, data, encoding):
    '''Builds a response object from the data returned by ftplib, using the
    specified encoding.'''
    response = Response()

    response.encoding = encoding

    # Fill in some useful fields.
    response.raw = data
    response.url = request.url
    response.request = request

    # Make sure to seek the file-like raw object back to the start.
    response.raw.seek(0)

    # Run the response hook.
    response = dispatch_hook('response', request.hooks, response)
    return response


class FTPAdapter(BaseAdapter):
    '''A Requests Transport Adapter that handles FTP urls.'''
    def __init__(self):
        super(FTPAdapter, self).__init__()

        # Build a dictionary keyed off the methods we support in upper case.
        # The values of this dictionary should be the functions we use to
        # send the specific queries.
        self.func_table = {'LIST': self.list,
                           'RETR': None,
                           'STOR': None,
                           'NLST': None}

    def send(self, request, **kwargs):
        '''Sends a PreparedRequest object over FTP. Returns a response object.
        '''
        # Get the authentication from the prepared request, if any.
        auth = self.get_username_password_from_header(request)

        # Next, get the host and the path.
        host, port, path = self.get_host_and_path_from_url(request)

        # Sort out the timeout.
        timeout = kwargs.get('timeout', None)

        # Establish the connection and login if needed.
        self.conn = ftplib.FTP()
        self.conn.connect(host, port, timeout)

        if auth is not None:
            self.conn.login(auth[0], auth[1])

        # Get the method and attempt to find the function to call.
        resp = self.func_table[request.method](path, request)

        # Return the response.
        return resp

    def close(self):
        '''Dispose of any internal state.'''
        raise NotImplementedError('Not yet implemented.')

    def list(self, path, request):
        '''Executes the FTP LIST command on the given path.'''
        data = StringIO()

        # To ensure the StringIO gets cleaned up, we need to alias its close
        # method to the release_conn() method. This is a dirty hack, but there
        # you go.
        data.release_conn = data.close

        self.conn.cwd(path)
        self.conn.retrbinary('LIST', data_callback_factory(data))

        # When that call has finished executing, we'll have all our data.
        response = build_text_response(request, data)

        return response

    def get_username_password_from_header(self, request):
        '''Given a PreparedRequest object, reverse the process of adding HTTP
        Basic auth to obtain the username and password. Allows the FTP adapter
        to piggyback on the basic auth notation without changing the control
        flow.'''
        auth_header = request.headers.get('Authorization')

        if auth_header:
            # The basic auth header is of the form 'Basic xyz'. We want the
            # second part. Check that we have the right kind of auth though.
            encoded_components = auth_header.split()[:2]
            if encoded_components[0] != 'Basic':
                raise AuthError('Invalid form of Authentication used.')
            else:
                encoded = encoded_components[1]

            # Decode the base64 encoded string.
            decoded = base64.b64decode(encoded)

            # The string is of the form 'username:password'. Split on the
            # colon.
            components = decoded.split(':')
            username = components[0]
            password = components[1]
            return (username, password)
        else:
            # No auth header. Return None.
            return None

    def get_host_and_path_from_url(self, request):
        '''Given a PreparedRequest object, split the URL in such a manner as to
        determine the host and the path. This is a separate method to wrap some
        of urlparse's craziness.'''
        url = request.url
        # scheme, netloc, path, params, query, fragment = urlparse(url)
        parsed = urlparse(url)
        path = parsed.path

        # If there is a slash on the front of the path, chuck it.
        if path[0] == '/':
            path = path[1:]

        host = parsed.hostname
        port = parsed.port

        return (host, port, path)


class AuthError(Exception):
    '''Denotes an error with authentication.'''
    pass
