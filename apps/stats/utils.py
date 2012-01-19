# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.sites.models import Site
from piwik.django.models import PiwikSite
from django.conf import settings
import logging
from functools import update_wrapper
import httplib
import urlparse
import urllib
from random import random
from inspect import isclass

logger = logging.getLogger(__name__)


def piwik_url(**kw):
    url = settings.PIWIK_URL + u"/piwik.php?"
    url += u'&'.join([k + u"=" + str(v) for k, v in kw.items()])
    logger.info("piwik url: %s" % url)
    return url

PIWIK_API_VERSION = 1


# Retrieve piwik information
_host = urlparse.urlsplit(settings.PIWIK_URL).netloc
try:
    _id_piwik = PiwikSite.objects.get(site=Site.objects.get_current().id).id_site
except PiwikSite.DoesNotExist:
    logger.debug("No PiwikSite is configured.")
    _id_piwik = None

def piwik_track(klass_or_method):
    """Track decorated class or method using Piwik (according to configuration in settings and django-piwik)
    Works for handler classes (executed by __call__) or handler methods. Expects request to be the first parameter
    """
    if _id_piwik is None:
        return klass_or_method

    # get target method
    if isclass(klass_or_method):
        klass = klass_or_method
        call_func = klass.__call__
    else:
        call_func = klass_or_method

    def wrap(self, request, *args, **kw):
        conn = httplib.HTTPConnection(_host)
        conn.request('GET', piwik_url(
            rec=1,
            apiv=PIWIK_API_VERSION,
            rand=int(random() * 0x10000),
            token_auth=urllib.quote(settings.PIWIK_TOKEN),
            cip=urllib.quote(request.META['REMOTE_ADDR']),
            url=urllib.quote('http://' + request.META['HTTP_HOST'] + request.path),
            urlref=urllib.quote(request.META['HTTP_REFERER']) if 'HTTP_REFERER' in request.META else '',
            idsite=_id_piwik))

        conn.close()
        return call_func(self, request, *args, **kw)

    # and wrap it
    update_wrapper(wrap, call_func)

    if isclass(klass_or_method):
        klass.__call__ = wrap
        return klass
    else:
        print klass_or_method
        return wrap
