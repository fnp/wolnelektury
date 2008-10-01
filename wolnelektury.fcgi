#!/usr/bin/env python
from os.path import abspath, dirname, join
import sys

# Redirect sys.stdout to sys.stderr for bad libraries like geopy that use
# print statements for optional import exceptions.
sys.stdout = sys.stderr

# Add apps and lib directories to PYTHONPATH
sys.path.insert(0, abspath(join(dirname(__file__), '../apps')))
sys.path.insert(0, abspath(join(dirname(__file__), '../lib')))

# Emulate manage.py path hacking.
sys.path.insert(0, abspath(join(dirname(__file__), "../../")))
sys.path.insert(0, abspath(join(dirname(__file__), "../")))

# Run Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method='threaded', daemonize='false')

