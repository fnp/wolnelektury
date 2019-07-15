# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os import path
from .paths import PROJECT_DIR

DEBUG = False
MAINTENANCE_MODE = False

ADMINS = [
    # ('Your Name', 'your_email@domain.com'),
]

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 'postgresql_psycopg2'
        'NAME': path.join(PROJECT_DIR, 'dev.db'),
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
    }
}

SOLR = "http://localhost:8983/solr/wl/"
SOLR_TEST = "http://localhost:8983/solr/wl_test/"
SOLR_STOPWORDS = "/path/to/solr/data/conf/lang/stopwords_pl.txt"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'
USE_TZ = True

SITE_ID = 1

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {
        'loaders': (
            ('django.template.loaders.cached.Loader', (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            )),
        ),
        'context_processors': (
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.request',
            'wolnelektury.context_processors.extra_settings',
            'search.context_processors.search_form',
        ),
    },
}]

MIDDLEWARE_CLASSES = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'ssify.middleware.SsiMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'ssify.middleware.PrepareForCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'fnp_django_pagination.middleware.PaginationMiddleware',
    'ssify.middleware.LocaleMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'fnpdjango.middleware.SetRemoteAddrFromXRealIP',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'wolnelektury.urls'
