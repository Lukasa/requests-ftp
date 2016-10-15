# -*- encoding: utf-8 -*-
from requests_ftp import ftp


def test_simple_welcome():
    assert ftp.get_status_code_from_code_response('200 Welcome') == 200


def test_ftp_retr_multiline_resp():
    '''
    Example from NASA:
        ftp://lasco6.nascom.nasa.gov/pub/lasco/lastimage
        /lastimg_C2.gif
    The code received is:
        '226-File successfully transferred\n226 0.000 seconds'
    '''
    assert ftp.get_status_code_from_code_response(
        '226-File successfully transferred\n226 0.000 seconds') == 226


def test_ftp_retr_multiline_resp_inconsistent_code():
    assert ftp.get_status_code_from_code_response(
        '200-File successfully transferred\n226 0.000 seconds') == 226