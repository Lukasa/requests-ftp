#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

APP_NAME = 'requests-ftp'
VERSION = '0.3.0'
AUTHOR = 'Cory Benfield'
LICENSE = 'Apache 2.0'

try:
    LONG_DESC = open('README.rst').read()
except IOError:
    LONG_DESC = ''

# This wrapper stolen wholesale from Requests.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = ['requests']

settings = dict()

settings.update(
    name=APP_NAME,
    version=VERSION,
    description='FTP Transport Adapter for Requests.',
    long_description=LONG_DESC,
    author=AUTHOR,
    author_email='cory@lukasa.co.uk',
    url='http://github.com/Lukasa/requests-ftp',
    packages=['requests_ftp'],
    package_data={'': ['LICENSE', 'AUTHORS', 'README.rst']},
    package_dir={'requests_ftp': 'requests_ftp'},
    include_package_data=True,
    install_requires=requires,
    license=LICENSE,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        ),
    )

setup(**settings)
