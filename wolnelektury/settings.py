# -*- coding: utf-8 -*-
# Django settings for wolnelektury project.
from os import path

PROJECT_DIR = path.abspath(path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG
MAINTENANCE_MODE = False

ADMINS = [
    # ('Your Name', 'your_email@domain.com'),
]

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': path.join(PROJECT_DIR, 'dev.db'), # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pl'

gettext = lambda s: s

LANGUAGES = tuple(sorted([
    ('pl', u'polski'),
    ('de', u'Deutsch'),
    ('en', u'English'),
    ('lt', u'lietuvių'),
    ('fr', u'français'),
    ('ru', u'русский'),
    ('es', u'español'),
    ('uk', u'українська'),
], key=lambda x: x[0]))


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path.join(PROJECT_DIR, '../media')
STATIC_ROOT = path.join(PROJECT_DIR, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'wolnelektury.context_processors.extra_settings',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'piwik.django.middleware.PiwikMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'wolnelektury.urls'

TEMPLATE_DIRS = [
    path.join(PROJECT_DIR, 'templates'),
]

LOGIN_URL = '/uzytkownicy/zaloguj/'

LOGIN_REDIRECT_URL = '/'

INSTALLED_APPS = [
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # external
    'south',
    'sorl.thumbnail',
    'sponsors',
    'newtagging',
    'pagination',
    'chunks',
    'compress',
    'modeltranslation',
    'catalogue',
    'lessons',
    'piston',
    'api',
    'rosetta',
    'infopages',
    'suggest',
    'lesmianator',
    'opds',
    'pdcounter',
    'piwik.django',
]

#CACHE_BACKEND = 'locmem:///?max_entries=3000'
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True

# CSS and JavaScript file groups
COMPRESS_CSS = {
    'all': {
        'source_filenames': ('css/master.css', 'css/jquery.autocomplete.css', 'css/jquery.countdown.css', 'css/master.plain.css', 'css/sponsors.css', 'css/facelist_2-0.css',),
        'output_filename': 'css/all.min?.css',
    },
    'book': {
        'source_filenames': ('css/master.book.css',),
        'output_filename': 'css/book.min?.css',
    }
}

COMPRESS_JS = {
    'jquery': {
        'source_filenames': ('js/jquery.js',),
        'output_filename': 'js/jquery.min.js',
    },
    'all': {
        'source_filenames': ('js/jquery.autocomplete.js', 'js/jquery.form.js',
            'js/jquery.countdown.js', 'js/jquery.countdown-pl.js',
            'js/jquery.countdown-de.js', 'js/jquery.countdown-uk.js',
            'js/jquery.countdown-es.js', 'js/jquery.countdown-lt.js',
            'js/jquery.countdown-ru.js', 'js/jquery.countdown-fr.js',
            'js/jquery.cycle.min.js',
            'js/jquery.jqmodal.js', 'js/jquery.labelify.js', 'js/catalogue.js',
            ),
        'output_filename': 'js/all?.min.js',
    },
    'book': {
        'source_filenames': ('js/jquery.eventdelegation.js', 'js/jquery.scrollto.js', 'js/jquery.highlightfade.js', 'js/book.js',),
        'output_filename': 'js/book?.min.js',
    },
    'book_ie': {
        'source_filenames': ('js/ierange-m2.js',),
        'output_filename': 'js/book_ie?.min.js',
    }

}

COMPRESS_VERSION = True
COMPRESS_CSS_FILTERS = None

THUMBNAIL_QUALITY = 95
THUMBNAIL_EXTENSION = 'png'

THUMBNAIL_PROCESSORS = (
    # Default processors
    'sorl.thumbnail.processors.colorspace',
    'sorl.thumbnail.processors.autocrop',
    'sorl.thumbnail.processors.scale_and_crop',
    'sorl.thumbnail.processors.filters',
    # Custom processors
    'sponsors.processors.add_padding',
)

TRANSLATION_REGISTRY = "wolnelektury.translation"


# seconds until a changes appears in the changes api
API_WAIT = 100

# limit number of filtering tags
MAX_TAG_LIST = 6

NO_BUILD_EPUB = False
NO_BUILD_TXT = False

# Load localsettings, if they exist
try:
    from localsettings import *
except ImportError:
    pass

