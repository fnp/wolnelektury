# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os.path import abspath, join
from django.conf import settings

try:
    WAITER_ROOT = abspath(settings.WAITER_ROOT)
except AttributeError:
    WAITER_ROOT = abspath(join(settings.MEDIA_ROOT, 'waiter'))

try:
    WAITER_URL = settings.WAITER_URL
except AttributeError:
    WAITER_URL = join(settings.MEDIA_URL, 'waiter')

try:
    WAITER_MAX_QUEUE = settings.WAITER_MAX_QUEUE
except AttributeError:
    WAITER_MAX_QUEUE = 20

