import sys
import os
from os import path

# Add project directories to PYTHONPATH
PROJECT_DIR = path.abspath(path.dirname(__file__))
PROJECT_MODULE_DIRS = [PROJECT_DIR + '/lib', PROJECT_DIR + '/apps', PROJECT_DIR + '/wolnelektury']

sys.path = PROJECT_MODULE_DIRS + sys.path


# Run Django
from django.core.handlers.wsgi import WSGIHandler

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
application = WSGIHandler()
