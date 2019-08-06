# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.

from machina import get_apps as get_machina_apps

INSTALLED_APPS_OUR = [
    'wolnelektury',
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
    'newsletter',
    'contact',
    'isbn',
    'paypal',
    'push',
]

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
    'admin_ordering',
    'rest_framework',
    'fnp_django_pagination',
    'pipeline',
    'piwik',
    'sorl.thumbnail',
    'honeypot',
    'fnpdjango',
    'getpaid',
    'getpaid.backends.payu',
    'django_extensions',
    'club.apps.ClubConfig',

    'debug_toolbar',

    # allauth stuff
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.twitter',

    # Machina related apps:
    'mptt',
    'haystack',
    'widget_tweaks',
] + get_machina_apps()

INSTALLED_APPS = INSTALLED_APPS_OUR + INSTALLED_APPS_CONTRIB
