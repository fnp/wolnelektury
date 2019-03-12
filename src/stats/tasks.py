# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from celery.task import task
from django.conf import settings
from http.client import HTTPConnection
import logging
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)


PIWIK_API_VERSION = 1

# Retrieve piwik information
try:
    _host = urlsplit(settings.PIWIK_URL).netloc
except AttributeError:
    logger.debug("PIWIK_URL not configured.")
    _host = None


@task(ignore_result=True)
def track_request(piwik_args):
    piwik_url = "%s%s%s" % (settings.PIWIK_URL, u"/piwik.php?", piwik_args)
    conn = HTTPConnection(_host)
    conn.request('GET', piwik_url)
    conn.close()
