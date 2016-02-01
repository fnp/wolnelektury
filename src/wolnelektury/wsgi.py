import os
import os.path
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add apps and lib directories to PYTHONPATH
sys.path = [
    os.path.join(ROOT, '../lib/librarian'),
] + sys.path


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wolnelektury.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
