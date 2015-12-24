# -*- coding: utf-8 -*-
# Django settings for wolnelektury project.
from os import path

from .basic import *
from .auth import *
from .cache import *
from .celery import *
from .contrib import *
from .custom import *
from .locale import *
from .static import *


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'wolnelektury_core.context_processors.extra_settings',
    'search.context_processors.search_form',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'ssify.middleware.SsiMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'ssify.middleware.PrepareForCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'ssify.middleware.LocaleMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'fnpdjango.middleware.SetRemoteAddrFromXRealIP',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'wolnelektury.urls'

# These are the ones we should test.
INSTALLED_APPS_OUR = [
    'wolnelektury_core',
    # our
    'ajaxable',
    'api',
    'catalogue',
    'chunks',
    'dictionary',
    'infopages',
    'lesmianator',
    'newtagging',
    'opds',
    'pdcounter',
    'reporting',
    'sponsors',
    'stats',
    'suggest',
    'picture',
    'social',
    'waiter',
    'search',
    'oai',
    'funding',
    'polls',
    'libraries',
    ]

GETPAID_BACKENDS = (
    'getpaid.backends.payu',
)

INSTALLED_APPS_CONTRIB = [
    # Should be before django.contrib.admin
    'modeltranslation',

    # external
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'pagination',
    'pipeline',
    'piston',
    'piwik',
    'sorl.thumbnail',
    'kombu.transport.django',
    'honeypot',
    'fnpdjango',
    'getpaid',
    'getpaid.backends.payu',
    'ssify',

    #allauth stuff
    'uni_form',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.facebook',
    #'allauth.socialaccount.providers.twitter',
    ]

INSTALLED_APPS = INSTALLED_APPS_OUR + INSTALLED_APPS_CONTRIB

# Load localsettings, if they exist
try:
    from wolnelektury.localsettings import *
except ImportError:
    pass
