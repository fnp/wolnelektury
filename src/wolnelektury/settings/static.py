# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os import path
from .paths import VAR_DIR

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path.join(VAR_DIR, 'media/')
STATIC_ROOT = path.join(VAR_DIR, 'static/')
SEARCH_INDEX = path.join(VAR_DIR, 'search_index/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

IMAGE_DIR = 'book/pictures/'

# CSS and JavaScript file groups

PIPELINE = {
    'STYLESHEETS': {
        'main': {
            # styles both for mobile and for big screen
            'source_filenames': [
                'css/jquery.countdown.css',
                'jplayer/jplayer.blue.monday.css',

                'sponsors/css/sponsors.css',

                'css/annoy.css',

                'css/ui-lightness/jquery-ui-1.8.16.custom.css',

                'css/tlite.css',

                'scss/main.scss',
            ],
            'output_filename': 'css/compressed/main.css',
        },
        'book': {
            'source_filenames': [
                'css/master.book.css',
            ],
            'output_filename': 'css/compressed/book.css',
        },
        'book_text': {
            'source_filenames': [
                'scss/book_text.scss',
                'css/new.book.css',
                'css/annoy.css',

                'css/master.picture.css',
            ],
            'output_filename': 'css/compressed/book_text.css',
        },
        'picture': {
            'source_filenames': [
                'css/master.book.css',
                'css/master.picture.css',
            ],
            'output_filename': 'css/compressed/picture.css',
        },
        'player': {
            'source_filenames': [
                'jplayer/jplayer.blue.monday.css',
                'player/player.css',
            ],
            'output_filename': 'css/compressed/player.css',
        },
        'simple': {
            'source_filenames': ('css/simple.css',),
            'output_filename': 'css/compressed/simple.css',
        },
        'widget': {
            'source_filenames': ('scss/widget.scss',),
            'output_filename': 'css/compressed/widget.css',
        },
    },
    'JAVASCRIPT': {
        'base': {
            'source_filenames': (
                'js/contrib/jquery.cycle.min.js',
                'js/contrib/jquery.jqmodal.js',
                'js/contrib/jquery.form.js',
                'js/contrib/jquery.paging.min.js',
                'js/contrib/jquery.countdown.js', 'js/contrib/jquery.countdown-pl.js',
                'js/contrib/jquery.countdown-de.js', 'js/contrib/jquery.countdown-uk.js',
                'js/contrib/jquery.countdown-es.js', 'js/contrib/jquery.countdown-lt.js',
                'js/contrib/jquery.countdown-ru.js', 'js/contrib/jquery.countdown-fr.js',
                'js/contrib/jquery.shorten.js',

                'js/contrib/jquery-ui-1.8.16.custom.min.js',

                'js/contrib/tlite.min.js',

                'jplayer/jquery.jplayer.min.js',
                'jplayer/jplayer.playlist.min.js',
                'player/player.js',

                'js/locale.js',
                'js/dialogs.js',
                'js/base.js',
                'pdcounter/pdcounter.js',
                'sponsors/js/sponsors.js',
                'player/openplayer.js',
                'js/search.js',
                'funding/funding.js',
                'club/form.js',

                'js/annoy.js',
                ),
            'output_filename': 'js/base.min.js',
        },
        'player': {
            'source_filenames': [
                'jplayer/jquery.jplayer.min.js',
                'jplayer/jplayer.playlist.min.js',
                'player/player.js',
            ],
            'output_filename': 'js/player.min.js',
        },
        'book': {
            'source_filenames': [
                'js/contrib/jquery.eventdelegation.js',
                'js/contrib/jquery.scrollto.js',
                'js/contrib/jquery.highlightfade.js',
                'js/book_text/other.js',
                'js/book.js',

                'js/contrib/raphael-min.js',
                'js/contrib/progressSpin.min.js',
                'js/picture.js',
            ],
            'output_filename': 'js/book.min.js',
        },
        'book_text': {
            'source_filenames': [
                'js/contrib/jquery.form.js',
                'js/contrib/jquery.jqmodal.js',
                'js/book_text/info.js',
                'js/book_text/menu.js',
                'js/book_text/note.js',
                'js/book_text/settings.js',
                'js/book_text/toc.js',
                'js/locale.js',
                'js/dialogs.js',

                'js/contrib/jquery.highlightfade.js',
                'js/contrib/raphael-min.js',
                'player/openplayer.js',
                'js/contrib/progressSpin.min.js',
                'js/annoy.js',
            ],
            'output_filename': 'js/book_text.js',
        },
        'picture': {
            'source_filenames': [
                'js/picture.js',
            ],
            'output_filename': 'js/picture.min.js',
        }
        'book_ie': {
            'source_filenames': ('js/contrib/ierange-m2.js',),
            'output_filename': 'js/book_ie.min.js',
        },
        'widget': {
            'source_filenames': (
                'js/contrib/jquery.js',
                'js/contrib/jquery-ui-1.8.16.custom.min.js',
                'js/search.js',
                'js/widget_run.js',
            ),
            'output_filename': 'js/widget.min.js',
        },
    },
    'CSS_COMPRESSOR': None,
    'JS_COMPRESSOR': 'pipeline.compressors.jsmin.JSMinCompressor',
    'COMPILERS': (
        'pipeline.compilers.sass.SASSCompiler',
        # We could probably use PySCSS instead,
        # but they have some serious problems, like:
        # https://github.com/Kronuz/pyScss/issues/166 (empty list syntax)
        # https://github.com/Kronuz/pyScss/issues/258 (bad @media order)
        # 'pyscss_compiler.PySCSSCompiler',
    )
}

STATICFILES_STORAGE = 'fnpdjango.pipeline_storage.GzipPipelineCachedStorage'
#STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

# PIPELINE_PYSCSS_BINARY = '/usr/bin/env pyscss'
# PIPELINE_PYSCSS_ARGUMENTS = ''


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.CachedFileFinder',
    'pipeline.finders.PipelineFinder',
]
