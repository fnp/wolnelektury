#!/usr/bin/env python
import os.path
import sys

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Add apps and lib directories to PYTHONPATH
sys.path = [
    os.path.join(ROOT, 'apps'),
    os.path.join(ROOT, 'lib'),
    os.path.join(ROOT, 'lib/librarian'),
] + sys.path

from django.core.management import execute_manager

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
