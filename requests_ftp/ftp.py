# -*- encoding: utf-8 -*-
from requests.adapters import BaseAdapter
import ftplib
import base64


class FTPAdapter(BaseAdapter):
    '''A Requests Transport Adapter that handles FTP urls.'''
    def __init__(self):
        super(FTPAdapter, self).__init__()

        # Currently there's no connection pooling here, so we don't need to
        # maintain any state.

    def send(self, request, **kwargs):
        '''Sends a PreparedRequest object over FTP. Returns a response object.
        '''
        raise NotImplementedError('Not yet implemented.')

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


class AuthError(Exception):
    '''Denotes an error with authentication.'''
    pass