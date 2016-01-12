# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import absolute_import

import os
import sys

from celery import Celery
from django.conf import settings

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path = [
    os.path.join(ROOT, 'lib/librarian'),
] + sys.path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wolnelektury.settings')

app = Celery('wolnelektury')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
