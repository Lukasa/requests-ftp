# -*- encoding: utf-8 -*-
from requests.adapters import BaseAdapter
import ftplib
import base64
from requests.compat import urlparse


class FTPAdapter(BaseAdapter):
    '''A Requests Transport Adapter that handles FTP urls.'''
    def __init__(self):
        super(FTPAdapter, self).__init__()

        # Currently there's no connection pooling here, so we don't need to
        # maintain any state.

    def send(self, request, **kwargs):
        '''Sends a PreparedRequest object over FTP. Returns a response object.
        '''
        # Get the authentication from the prepared request, if any.
        auth = self.get_username_password_from_header(request)

        # Next, get the host and the path.
        host, path = self.get_host_and_path_from_url(request)

        # Establish the connection and login if needed.
        self.conn = ftplib.FTP(host)

        if auth is not None:
            self.conn.login(auth[0], auth[1])

    def close(self):
        '''Dispose of any internal state.'''
        raise NotImplementedError('Not yet implemented.')

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
        scheme, netloc, path, params, query, fragment = urlparse(url)

        # urlparse is _very_ touchy about the format of a URL, which means that
        # sometimes it assumes there is no netloc. I disagree with it, so we
        # need to work around that.
        if not netloc:
            # Urlparse is wrong. Simply split the path on the first /, and
            # treat everything before that as the netloc. Then rebuild the path
            # by joining it with slashes.
            components = path.split('/')
            netloc = components[0]
            path = '/'.join(components[1:])

            # If there is a slash on the front, chuck it.
            if path[0] == '/':
                path = path[1:]

        return (netloc, path)


class AuthError(Exception):
    '''Denotes an error with authentication.'''
    pass
