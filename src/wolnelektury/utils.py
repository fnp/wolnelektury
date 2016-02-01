# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os
import pytz
from django.utils import timezone
from django.conf import settings

tz = pytz.timezone(settings.TIME_ZONE)


def localtime_to_utc(localtime):
    return timezone.utc.normalize(
        tz.localize(localtime)
    )


def utc_for_js(dt):
    return dt.strftime('%Y/%m/%d %H:%M:%S UTC')


def makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)
