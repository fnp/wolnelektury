
from django.contrib.sites.models import Site
from piwik.django.models import PiwikSite
from django.conf import settings
import logging
from functools import update_wrapper
import httplib
import urlparse
from random import random

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def piwik_url(**kw):
    url = settings.PIWIK_URL + u"/piwik.php?"
    url += u'&'.join([k + u"=" + str(v) for k, v in kw.items()])
    return url

PIWIK_API_VERSION = 1


def piwik_track(klass):
    current_site = Site.objects.get_current()
    piwik_site = PiwikSite.objects.filter(site=current_site.id)

    if len(piwik_site) == 0:
        logger.warn("No PiwikSite is configured for Site " + current_site.name)
        return klass

    id_piwik = piwik_site[0].id_site
    call_func = klass.__call__
    host = urlparse.urlsplit(settings.PIWIK_URL).netloc

    def wrap(self, request, *args, **kw):
        conn = httplib.HTTPConnection(host)
        conn.request('GET', piwik_url(
            rec=1,
            apiv=PIWIK_API_VERSION,
            rand=int(random() * 0x10000),
            cip=request.META['REMOTE_ADDR'],
            url='http://' + request.META['HTTP_HOST'] + request.path,
            urlref=request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else '',
            idsite=id_piwik))

        conn.close()
        return call_func(self, request, *args, **kw)

    update_wrapper(wrap, call_func)
    klass.__call__ = wrap

    return klass
