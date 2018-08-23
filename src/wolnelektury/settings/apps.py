# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
# These are the ones we should test.
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
    'fnp_django_pagination',
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
    'django_extensions',
    'raven.contrib.django.raven_compat',

    'migdal',
    'django_comments',
    'django_comments_xtd',

    # allauth stuff
    'uni_form',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.twitter',
]

INSTALLED_APPS = INSTALLED_APPS_OUR + INSTALLED_APPS_CONTRIB
