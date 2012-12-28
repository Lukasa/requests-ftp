# -*- encoding: utf-8 -*-
from requests.adapters import BaseAdapter


class FTPAdapter(BaseAdapter):
    '''A Requests Transport Adapter that handles FTP urls.'''
    def __init__(self):
        super(FTPAdapter, self).__init__()

    def send(self):
        '''Sends a PreparedRequest object over FTP. Returns a response object.
        '''
        raise NotImplementedError('Not yet implemented.')

    def close(self):
        '''Dispose of any internal state.'''
        raise NotImplementedError('Not yet implemented.')
