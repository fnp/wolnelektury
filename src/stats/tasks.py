# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from celery import shared_task
from django.conf import settings
import logging
from urllib.parse import urlsplit
from urllib.request import urlopen


logger = logging.getLogger(__name__)


PIWIK_API_VERSION = 1

# Retrieve piwik information
try:
    _host = urlsplit(settings.PIWIK_URL).netloc
except AttributeError:
    logger.debug("PIWIK_URL not configured.")
    _host = None


@shared_task(ignore_result=True)
def track_request(piwik_args):
    urlopen("%s%s%s" % (settings.PIWIK_URL, "piwik.php?", piwik_args))
