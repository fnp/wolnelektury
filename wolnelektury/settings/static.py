from os import path
from .paths import PROJECT_DIR

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path.join(PROJECT_DIR, '../media/')
STATIC_ROOT = path.join(PROJECT_DIR, '../static/')
SEARCH_INDEX = path.join(PROJECT_DIR, '../search_index/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

# CSS and JavaScript file groups


PIPELINE_CSS = {
    'main': {
        # styles both for mobile and for big screen
        'source_filenames': [
            'css/jquery.countdown.css', 

            'sponsors/css/sponsors.css',
            'css/social/shelf_tags.css',

            'uni_form/uni-form.css',
            'uni_form/default.uni-form.css',

            'css/ui-lightness/jquery-ui-1.8.16.custom.css',

            'scss/all.scss',
        ],
        'output_filename': 'css/compressed/main.css',
    },
    'book': {
        'source_filenames': [
            'css/master.book.css',
        ],
        'output_filename': 'css/compressed/book.css',
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
}

PIPELINE_JS = {
    'base': {
        'source_filenames': (
            'js/jquery.cycle.min.js',
            'js/jquery.jqmodal.js',
            'js/jquery.form.js',
            'js/jquery.countdown.js', 'js/jquery.countdown-pl.js',
            'js/jquery.countdown-de.js', 'js/jquery.countdown-uk.js',
            'js/jquery.countdown-es.js', 'js/jquery.countdown-lt.js',
            'js/jquery.countdown-ru.js', 'js/jquery.countdown-fr.js',

            'js/jquery-ui-1.8.16.custom.min.js',

            'js/locale.js',
            'js/dialogs.js',
            'js/base.js',
            'pdcounter/pdcounter.js',
            'sponsors/js/sponsors.js',
            'player/openplayer.js',
            'js/search.js',
            'funding/funding.js',
            
            'uni_form/uni-form.js',
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
            'js/jquery.eventdelegation.js',
            'js/jquery.scrollto.js',
            'js/jquery.highlightfade.js',
            'js/book.js',
            'player/openplayer.js',
        ],
        'output_filename': 'js/book.min.js',
    },
    'book_ie': {
        'source_filenames': ('js/ierange-m2.js',),
        'output_filename': 'js/book_ie.min.js',
    }

}

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
PIPELINE_CSS_COMPRESSOR = None
PIPELINE_JS_COMPRESSOR = None

PIPELINE_COMPILERS = (
    'pyscss_compiler.PySCSSCompiler',
)
PIPELINE_PYSCSS_BINARY = '/usr/bin/env pyscss'
PIPELINE_PYSCSS_ARGUMENTS = ''
