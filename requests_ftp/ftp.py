# -*- encoding: utf-8 -*-
from requests.adapters import BaseAdapter


class FTPAdapter(BaseAdapter):
    '''A Requests Transport Adapter that handles FTP urls.'''
    def __init__(self):
        super(FTPAdapter, self).__init__()

    def send(self):
        raise NotImplementedError('Not yet implemented.')

    def close(self):
        raise NotImplementedError('Not yet implemented.')
