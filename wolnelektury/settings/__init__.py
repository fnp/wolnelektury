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
    "allauth.context_processors.allauth",
    "allauth.account.context_processors.account",
)

MIDDLEWARE_CLASSES = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'piwik.django.middleware.PiwikMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'fnpdjango.middleware.SetRemoteAddrFromXRealIP',
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
    ]

INSTALLED_APPS_CONTRIB = [
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
    'piwik.django',
    #'rosetta',
    'south',
    'sorl.thumbnail',
    'djcelery',
    'djkombu',
    'honeypot',
    #'django_nose',

    #allauth stuff
    'emailconfirmation',
    'uni_form',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.openid',
    #'allauth.facebook',
    #'allauth.twitter',

    # included
    'modeltranslation',
    ]

INSTALLED_APPS = INSTALLED_APPS_OUR + INSTALLED_APPS_CONTRIB

# Load localsettings, if they exist
try:
    from wolnelektury.localsettings import *
except ImportError:
    pass
