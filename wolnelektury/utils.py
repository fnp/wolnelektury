import pytz
from django.utils import timezone
from django.conf import settings

def localtime_to_utc(localtime):
    return timezone.utc.normalize(
        pytz.timezone(settings.TIME_ZONE).localize(localtime)
    )

def utc_for_js(dt):
    return dt.strftime('%Y/%m/%d %H:%M:%S UTC')
