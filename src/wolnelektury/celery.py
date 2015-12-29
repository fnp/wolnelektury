from __future__ import absolute_import

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path = [
    os.path.join(ROOT, 'apps'),
    os.path.join(ROOT, 'lib'),
    os.path.join(ROOT, 'lib/librarian'),
] + sys.path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wolnelektury.settings')

from celery import Celery
from django.conf import settings

app = Celery('wolnelektury')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
