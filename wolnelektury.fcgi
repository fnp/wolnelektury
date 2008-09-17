#!/usr/bin/python
import sys
import os
from os import path

# Add project directories to PYTHONPATH
PROJECT_DIR = path.abspath(path.dirname(__file__))
PROJECT_MODULE_DIRS = [PROJECT_DIR + '/lib', PROJECT_DIR + '/apps', PROJECT_DIR + '/wolnelektury']

sys.path = PROJECT_MODULE_DIRS + sys.path

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_eo'

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method='threaded', daemonize='false')

