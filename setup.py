#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import sys

import requests_ftp

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# This wrapper stolen wholesale from Requests.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = ['requests']

settings = dict()

settings.update(
    name=requests_ftp.__title__,
    version=requests_ftp.__version__,
    description='FTP Transport Adapter for Requests.',
    long_description=open('README.rst').read(),
    author=requests_ftp.__author__,
    author_email='cory@lukasa.co.uk',
    url='http://github.com/Lukasa/requests_ftp',
    packages=['requests_ftp'],
    package_data={'': ['LICENSE', 'AUTHORS']},
    package_dir={'requests_ftp': 'requests_ftp'},
    include_package_data=True,
    install_requires=requires,
    license=requests_ftp.__license__,
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
