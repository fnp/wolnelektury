# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.sites.models import Site
from piwik.django.models import PiwikSite
from django.conf import settings
from datetime import datetime
import logging
from functools import update_wrapper
import urllib
from random import random
from inspect import isclass
from .tasks import track_request

logger = logging.getLogger(__name__)


def piwik_url(request):
    return urllib.urlencode(dict(
        idsite=_id_piwik,
        rec=1,
        url='http://%s%s' % (request.META['HTTP_HOST'], request.path),
        rand=int(random() * 0x10000),
        apiv=PIWIK_API_VERSION,
        urlref=request.META.get('HTTP_REFERER', ''),
        ua=request.META.get('HTTP_USER_AGENT', ''),
        lang=request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
        token_auth=getattr(settings, 'PIWIK_TOKEN', ''),
        cip=request.META['REMOTE_ADDR'],
        cdt=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ))

PIWIK_API_VERSION = 1


# Retrieve piwik information
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
        track_request.delay(piwik_url(request))
        return call_func(self, request, *args, **kw)

    # and wrap it
    update_wrapper(wrap, call_func)

    if isclass(klass_or_method):
        klass.__call__ = wrap
        return klass
    else:
        return wrap
