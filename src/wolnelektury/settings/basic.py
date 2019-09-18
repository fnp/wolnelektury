# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os import path
from machina import MACHINA_MAIN_TEMPLATE_DIR
from .paths import PROJECT_DIR

DEBUG = True
MAINTENANCE_MODE = False

ADMINS = [
    # ('Your Name', 'your_email@domain.com'),
]

MANAGERS = ADMINS

CONTACT_EMAIL = 'fundacja@nowoczesnapolska.org.pl'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 'postgresql_psycopg2'
        'NAME': path.join(PROJECT_DIR, 'dev.db'),
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
    }
}

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
    'DIRS': (
        path.join(PROJECT_DIR, 'templates'),  # Duplicate, because of Machina<1 weird configuration.
        MACHINA_MAIN_TEMPLATE_DIR,
    ),
    'OPTIONS': {
        'loaders': (
            ('django.template.loaders.cached.Loader', (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            )),
        ),
        'context_processors': (
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.request',
            'wolnelektury.context_processors.extra_settings',
            'search.context_processors.search_form',
            'machina.core.context_processors.metadata',
        ),
    },
}]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'fnp_django_pagination.middleware.PaginationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'fnpdjango.middleware.SetRemoteAddrFromXRealIP',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'machina.apps.forum_permission.middleware.ForumPermissionMiddleware',
]

ROOT_URLCONF = 'wolnelektury.urls'

FILE_UPLOAD_PERMISSIONS = 0o640
