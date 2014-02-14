# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import pytz
from django.utils import timezone
from django.conf import settings
from pipeline.storage import GZIPMixin
from pipeline.storage import PipelineCachedStorage

tz = pytz.timezone(settings.TIME_ZONE)

def localtime_to_utc(localtime):
    return timezone.utc.normalize(
        tz.localize(localtime)
    )

def utc_for_js(dt):
    return dt.strftime('%Y/%m/%d %H:%M:%S UTC')

class GzipPipelineCachedStorage(GZIPMixin, PipelineCachedStorage):
    pass
