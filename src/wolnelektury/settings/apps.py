# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#

INSTALLED_APPS_OUR = [
    'wolnelektury',
    # our
    'ajaxable',
    'annoy',
    'api',
    'bookmarks',
    'catalogue',
    'chunks',
    'dictionary',
    'education',
    'experiments',
    'infopages',
    'lesmianator',
    'messaging',
    'newtagging',
    'opds',
    'pdcounter',
    'pz',
    'references',
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
    'club',
    'redirects',
]

INSTALLED_APPS_CONTRIB = [
    # Should be before django.contrib.admin
    'modeltranslation',

    # external
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'admin_ordering',
    'rest_framework',
    'django_filters',
    'fnp_django_pagination',
    'pipeline',
    'sorl.thumbnail',
    'honeypot',
    'fnpdjango',
    'django_extensions',
    'forms_builder.forms',
    'django_countries',

    'debug_toolbar',

    # allauth stuff
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.twitter',
]

INSTALLED_APPS = INSTALLED_APPS_OUR + INSTALLED_APPS_CONTRIB
