from os import path
from settings.paths import PROJECT_DIR

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path.join(PROJECT_DIR, '../media/')
STATIC_ROOT = path.join(PROJECT_DIR, 'static/')
SEARCH_INDEX = path.join(PROJECT_DIR, '../search_index/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# CSS and JavaScript file groups
COMPRESS_CSS = {
    'all': {
        #'source_filenames': ('css/master.css', 'css/jquery.autocomplete.css', 'css/master.plain.css', 'css/facelist_2-0.css',),
        'source_filenames': [
            'css/jquery.countdown.css', 

            'css/base.css',
            'css/cite.css',
            'css/header.css',
            'css/main_page.css',
            'css/dialogs.css',
            'css/picture_box.css',
            'css/book_box.css',
            'css/catalogue.css',
            'css/sponsors.css',
            'css/auth.css',

            'css/social/shelf_tags.css',
            'css/ui-lightness/jquery-ui-1.8.16.custom.css',
        ],
        'output_filename': 'css/all.min?.css',
    },
    'screen': {
        'source_filenames': ['css/screen.css'],
        'output_filename': 'css/screen.min?.css',
        'extra_context': {
            'media': 'screen and (min-width: 800px)',
        },
    },
    'ie': {
        'source_filenames': [
            'css/ie.css',
        ],
        'output_filename': 'css/ie.min?.css',
    },
    'book': {
        'source_filenames': [
            'css/master.book.css',
        ],
        'output_filename': 'css/book.min?.css',
    },
    'player': {
        'source_filenames': [
            'jplayer/jplayer.blue.monday.css', 
            'css/player.css', 
        ],
        'output_filename': 'css/player.min?.css',
    },
    'simple': {
        'source_filenames': ('css/simple.css',),
        'output_filename': 'css/simple.min?.css',
    },
}

COMPRESS_JS = {
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
            'js/sponsors.js',
            'js/base.js',
            'js/pdcounter.js',

            'js/search.js',
            ),
        'output_filename': 'js/base?.min.js',
    },
    'player': {
        'source_filenames': [
            'jplayer/jquery.jplayer.min.js', 
            'jplayer/jplayer.playlist.min.js', 
            'js/player.js', 
        ],
        'output_filename': 'js/player.min?.js',
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
