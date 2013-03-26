import datetime
import pytz
from django.conf import settings
from django import template
from django.utils import timezone


register = template.Library()

@register.filter
def local_to_utc(localtime):
    if isinstance(localtime, datetime.date):
        localtime = datetime.datetime.combine(localtime, datetime.time(0,0))
    return timezone.utc.normalize(
        pytz.timezone(settings.TIME_ZONE).localize(localtime)
    )


@register.filter
def utc_for_js(dt):
    return dt.strftime('%Y/%m/%d %H:%M:%S UTC')
