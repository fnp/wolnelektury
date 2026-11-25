# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import os
from .paths import VAR_DIR

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(VAR_DIR, 'media/')
STATIC_ROOT = os.path.join(VAR_DIR, 'static/')

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
                '2022/styles/reader_player.scss',
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
                #'js/contrib/jquery.scrollto.js',

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

                'js/book_text/pbox.js',
                'js/book_text/pbox-items.js',

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

                'js/contrib/jquery.scrollto.js',

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
    'JS_COMPRESSOR': 'pipeline.compressors.jsmin.JSMinCompressor',
    'COMPILERS': ('pipeline.compilers.sass.SASSCompiler',),
    'SASS_BINARY': '/opt/dart-sass/sass',
    'SASS_ARGUMENTS': '--embed-source-map --embed-sources',
    # Compress CSSwith a second run of dart-sass.
    'CSS_COMPRESSOR': 'pipeline.compressors.cssmin.CSSMinCompressor',
    'CSSMIN_BINARY': '/opt/dart-sass/sass',
    'CSSMIN_ARGUMENTS': '--stdin --style=compressed --no-source-map',
}


STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage'
    },
    'book': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
        'OPTIONS': {
            'allow_overwrite': True,
        },
    },
    'bookmedia': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
        'OPTIONS': {
            'allow_overwrite': True,
        },
    },
    'staticfiles': {
        'BACKEND': 'fnpdjango.pipeline_storage.GzipPipelineManifestStorage'
    },
}


# Switch bookmedia to s3 if set.
WL_BOOKMEDIA_STORAGE_MODE = os.environ.get(
    "WL_BOOKMEDIA_STORAGE_MODE", "local") # or s3

if WL_BOOKMEDIA_STORAGE_MODE == "s3":
    AWS_S3_REGION_NAME = os.environ.get("WL_S3_REGION", "waw")
    AWS_S3_ENDPOINT_URL = os.environ.get(
        "WL_S3_ENDPOINT", f"https://s3.{AWS_S3_REGION_NAME}.io.cloud.ovh.net"
    )
    WL_S3_BUCKET = os.environ.get("WL_S3_BUCKET")
    STORAGES['bookmedia'] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": WL_S3_BUCKET,
            "access_key": os.environ.get("WL_S3_ACCESS_KEY"),
            "secret_key": os.environ.get("WL_S3_SECRET_KEY"),
            "custom_domain": os.environ.get(
                "WL_S3_CUSTOM_DOMAIN",
                f"{WL_S3_BUCKET}.s3.{AWS_S3_REGION_NAME}.io.cloud.ovh.net"
            ),
            "default_acl": "public-read",
            "querystring_auth": False,
            "file_overwrite": True,
        }
    }



STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.CachedFileFinder',
    'pipeline.finders.PipelineFinder',
]
