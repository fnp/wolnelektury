# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

INSTALLED_APPS_OUR = [
    'wolnelektury',
    # our
    'ajaxable',
    'annoy',
    'api',
    'catalogue',
    'chunks',
    'dictionary',
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
    'club.apps.ClubConfig',
    'redirects.apps.RedirectsConfig',
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
    'admin_ordering',
    'rest_framework',
    'fnp_django_pagination',
    'pipeline',
    'sorl.thumbnail',
    'honeypot',
    'fnpdjango',
    'getpaid',
    'getpaid.backends.payu',
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

    # Machina dependencies:
    'mptt',
    'haystack',
    'widget_tweaks',

    # Machina apps:
    'machina',
    'machina.apps.forum',
    'machina.apps.forum_conversation',
    'machina.apps.forum_conversation.forum_attachments',
    'machina.apps.forum_conversation.forum_polls',
    'machina.apps.forum_feeds',
    'machina.apps.forum_moderation',
    'machina.apps.forum_search',
    'machina.apps.forum_tracking',
    'machina.apps.forum_member',
    'machina.apps.forum_permission',
]

INSTALLED_APPS = INSTALLED_APPS_OUR + INSTALLED_APPS_CONTRIB
