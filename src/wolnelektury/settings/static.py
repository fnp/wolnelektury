# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from os import path
from .paths import VAR_DIR

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path.join(VAR_DIR, 'media/')
STATIC_ROOT = path.join(VAR_DIR, 'static/')

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
            'source_filenames': [
                'contrib/jquery-ui-1.13.1.custom/jquery-ui.css',
                'css/jquery.countdown.css',

                '2022/styles/main.scss',
                '2022/more.scss',
                'chunks/edit.scss',

                'scss/text.scss',
            ],
            'output_filename': 'css/compressed/main.css',
        },
        'book_text': {
            'source_filenames': [
                'css/import/gelasio.css',

                'scss/book_text.scss',
                'css/new.book.css',

                'annoy/banner.scss',  # ?
                'annoy/book_text.scss',  # ?
                '2022/styles/reader_player.scss',  # ?

                'css/master.picture.css',
            ],
            'output_filename': 'css/compressed/book_text.css',
        },
        'widget': {
            'source_filenames': ('scss/widget.scss',),
            'output_filename': 'css/compressed/widget.css',
        },
    },
    'JAVASCRIPT': {
        'main': {
            'source_filenames': [
                '2022/scripts/vendor.js',
                'contrib/jquery-ui-1.13.1.custom/jquery-ui.js',

                'js/search.js',
                'js/header.js',
                'book/filter.js',
                'chunks/edit.js',
                '2022/scripts/modernizr.js',
                'js/main.js',

                'js/contrib/jquery.cycle2.min.js',
                'sponsors/js/sponsors.js',
                'annoy/banner.js',
                'js/book_text/info.js',
                'js/book_text/menu.js',
                'js/book_text/note.js',
                'js/book_text/references.js',
                'js/book_text/settings.js',
                'js/book_text/toc.js',
                'js/book_text/progress.js',

                'js/contrib/jquery.countdown.js', 'js/contrib/jquery.countdown-pl.js',
                'js/contrib/jquery.countdown-de.js', 'js/contrib/jquery.countdown-uk.js',
                'js/contrib/jquery.countdown-es.js', 'js/contrib/jquery.countdown-lt.js',
                'js/contrib/jquery.countdown-ru.js', 'js/contrib/jquery.countdown-fr.js',
                'pdcounter/pdcounter.js',

            ],
            'output_filename': 'js/compressed/main.min.js'
        },
        'player': {
            'source_filenames': [
                'js/contrib/jplayer/jquery.jplayer.min.js',
                'js/contrib/jplayer/jplayer.playlist.min.js',
                'player/player.js',
            ],
            'output_filename': 'js/compressed/player.min.js',
        },
        'book_text': {
            'source_filenames': [
                'js/contrib/jquery.form.js',
                'js/contrib/jquery.jqmodal.js',
                'js/book_text/info.js',
                'js/book_text/menu.js',
                'js/book_text/note.js',
                'js/book_text/references.js',
                'js/book_text/settings.js',
                'js/book_text/toc.js',
                'js/locale.js',
                'js/dialogs.js',
                'annoy/book_text.js',

                'js/contrib/jquery.highlightfade.js',
                'js/contrib/raphael-min.js',
                'js/contrib/progressSpin.min.js',
                'annoy/banner.js',
            ],
            'output_filename': 'js/book_text.js',
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
        'libsasscompiler.LibSassCompiler',
    )
}

STATICFILES_STORAGE = 'fnpdjango.pipeline_storage.GzipPipelineManifestStorage'

# PIPELINE_PYSCSS_BINARY = '/usr/bin/env pyscss'
# PIPELINE_PYSCSS_ARGUMENTS = ''


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.CachedFileFinder',
    'pipeline.finders.PipelineFinder',
]
