# -*- coding: utf-8 -*-
# Django settings for wolnelektury project.
from os import path

PROJECT_DIR = path.abspath(path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    (u'Marek Stępniowski', 'marek@stepniowski.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = path.join(PROJECT_DIR, 'lektury.sqlite')  # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pl'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_DIR + '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://localhost:8000/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
]

# If DEBUG is enabled add query log to bottom of every template
if DEBUG:
    MIDDLEWARE_CLASSES.append('middleware.ProfileMiddleware')

ROOT_URLCONF = 'wolnelektury.urls'

TEMPLATE_DIRS = (
    PROJECT_DIR + '/templates/'
)

# CSS and JS files to compress
COMPRESS_CSS = {
    'all': {
        'source_filenames': ('css/master.css', 'css/jquery.autocomplete.css',),
        'output_filename': 'css/all.min.css',
    }
}

COMPRESS_JS = {
    'all': {
        'source_filenames': ('js/jquery.js', 'js/jquery.autocolumn.js', 'js/jquery.autocomplete.js', 
            'js/jquery.form.js', 'js/jquery.jqmodal.js', 'js/jquery.labelify.js', 'js/catalogue.js',),
        'output_filename': 'js/all.min.js',
    }
}

COMPRESS_CSS_FILTERS = None

LOGIN_URL = '/uzytkownicy/zaloguj/'

LOGIN_REDIRECT_URL = '/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'newtagging',
    'pagination',
    'chunks',
    'compress',
    'catalogue',
)

