# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from fnpdjango.utils.text.textilepl import textile_pl
from migdal import EntryType
from django.utils.translation import ugettext_lazy as _

HONEYPOT_FIELD_NAME = 'miut'
PAGINATION_INVALID_PAGE_RAISES_404 = True
THUMBNAIL_QUALITY = 95

MODELTRANSLATION_DEFAULT_LANGUAGE = 'pl'
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'pl'

MIGRATION_MODULES = {
    'getpaid': 'wolnelektury.migrations.getpaid',
}

GETPAID_ORDER_DESCRIPTION = "{% load funding_tags %}{{ order|sanitize_payment_title }}"

GETPAID_BACKENDS = (
    'getpaid.backends.payu',
)

PIWIK_URL = ''
PIWIK_SITE_ID = 0
PIWIK_TOKEN = ''

PAYPAL_CONFIG = {
    'mode': 'sandbox',  # sandbox or live
    'client_id': '',
    'client_secret': '',
}

MARKUP_FIELD_TYPES = (
    ('textile_pl', textile_pl),
)

MIGDAL_TYPES = (
    EntryType('news', _('news'), commentable=False, on_main=True, promotable=True),
    EntryType('publications', _('publications'), commentable=False),
    EntryType('info', _('info'), commentable=False),
    EntryType('event', _('events'), commentable=False),
)

MIGDAL_OPTIONAL_LANGUAGES = (
    ('en', u'English'),
)

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'api.renderers.LegacyXMLRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.drf_auth.PistonOAuthAuthentication',
    )
}
