# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import datetime
import pytz
from django.conf import settings
from django import template
from django.utils import timezone


register = template.Library()


@register.filter
def date_to_utc(date, day_end=False):
    """ Converts a datetime.date to UTC datetime.

    The datetime represents the start (or end) of the given day in
    the server's timezone.
    """
    if day_end:
        date += datetime.timedelta(1)
    localtime = datetime.datetime.combine(date, datetime.time(0, 0))
    return timezone.utc.normalize(
        pytz.timezone(settings.TIME_ZONE).localize(localtime)
    )


@register.filter
def utc_for_js(dt):
    return dt.strftime('%Y/%m/%d %H:%M:%S UTC')
