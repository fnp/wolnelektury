# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings
from datetime import datetime
import logging
from functools import update_wrapper
from urllib.parse import urlencode
from random import random
from inspect import isclass

from django.utils.encoding import force_bytes

from .tasks import track_request

logger = logging.getLogger(__name__)


def piwik_url(request):
    return urlencode(dict(
        idsite=getattr(settings, 'PIWIK_SITE_ID', '0'),
        rec=1,
        url=force_bytes('http://%s%s' % (request.META['HTTP_HOST'], request.path)),
        rand=int(random() * 0x10000),
        apiv=PIWIK_API_VERSION,
        urlref=force_bytes(request.META.get('HTTP_REFERER', '')),
        ua=request.META.get('HTTP_USER_AGENT', ''),
        lang=request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
        token_auth=getattr(settings, 'PIWIK_TOKEN', ''),
        cip=request.META['REMOTE_ADDR'],
        cdt=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ))

PIWIK_API_VERSION = 1


def piwik_track(klass_or_method):
    """Track decorated class or method using Piwik (according to configuration in settings and django-piwik)
    Works for handler classes (executed by __call__) or handler methods. Expects request to be the first parameter
    """
    if not getattr(settings, 'PIWIK_SITE_ID', 0):
        return klass_or_method

    # get target method
    if isclass(klass_or_method):
        klass = klass_or_method
        call_func = klass.__call__
    else:
        call_func = klass_or_method

    def wrap(self, request, *args, **kw):
        if getattr(request, 'piwik_track', True):
            track_request.delay(piwik_url(request))
        return call_func(self, request, *args, **kw)

    # and wrap it
    update_wrapper(wrap, call_func)

    if isclass(klass_or_method):
        klass.__call__ = wrap
        return klass
    else:
        return wrap


def piwik_track_view(view):
    if not getattr(settings, 'PIWIK_SITE_ID', 0):
        return view

    def wrap(request, *args, **kwargs):
        if getattr(request, 'piwik_track', True):
            track_request.delay(piwik_url(request))
        return view(request, *args, **kwargs)

    update_wrapper(wrap, view)
    return wrap
