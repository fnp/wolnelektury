# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
HONEYPOT_FIELD_NAME = 'miut'
PAGINATION_INVALID_PAGE_RAISES_404 = True
THUMBNAIL_QUALITY = 95

MODELTRANSLATION_DEFAULT_LANGUAGE = 'pl'
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'pl'

PIWIK_URL = ''
PIWIK_SITE_ID = 0
PIWIK_TOKEN = ''

PAYPAL_CONFIG = {
    'mode': 'sandbox',  # sandbox or live
    'client_id': '',
    'client_secret': '',
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'api.renderers.LegacyXMLRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.drf_auth.PistonOAuthAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}


DEBUG_TOOLBAR_CONFIG = {
    'RESULTS_CACHE_SIZE': 100,
}


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}


FORMS_BUILDER_USE_SITES = False
FORMS_BUILDER_EDITABLE_FIELD_MAX_LENGTH = True
FORMS_BUILDER_EDITABLE_SLUGS = True
FORMS_BUILDER_EXTRA_FIELDS = [
        (100, 'contact.fields.HeaderField', 'Header'),
        (101, 'contact.fields.SeparatorField', 'Separator'),
]
FORMS_BUILDER_HELPTEXT_MAX_LENGTH = 2048
FORMS_BUILDER_REQUIRED_CSS_CLASS = 'required'
FORMS_BUILDER_INACTIVE_VISIBLE = True
FORMS_BUILDER_TEMPLATE_NAME_P = 'forms/p.html'
