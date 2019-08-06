# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.utils.translation import ugettext_lazy as _

LICENSES = {
    'http://creativecommons.org/licenses/by-sa/3.0/': {
        'icon': 'cc-by-sa',
        'description': _('Creative Commons Attribution-ShareAlike 3.0 Unported'),
    },
    'http://artlibre.org/licence/lal/pl/': {
        'icon': 'lal',
        'description': _('Free Art License 1.3'),
    }
}
LICENSES['http://creativecommons.org/licenses/by-sa/3.0/deed.pl'] = \
    LICENSES['http://creativecommons.org/licenses/by-sa/3.0/']


for license, data in list(LICENSES.items()):
    LICENSES[license.replace('http://', 'https://')] = data

# Those will be generated only for books with own HTML.
EBOOK_FORMATS_WITHOUT_CHILDREN = ['txt', 'fb2']
# Those will be generated for all books.
EBOOK_FORMATS_WITH_CHILDREN = ['pdf', 'epub', 'mobi']
# Those will be generated when inherited cover changes.
EBOOK_FORMATS_WITH_COVERS = ['pdf', 'epub', 'mobi']

EBOOK_FORMATS = EBOOK_FORMATS_WITHOUT_CHILDREN + EBOOK_FORMATS_WITH_CHILDREN

EBOOK_CONTENT_TYPES = {
    'html': 'text/html',
    'pdf': 'application/pdf',
    'txt': 'text/plain',
    'epub': 'application/epub+zip',
    'mobi': 'application/x-mobipocket-ebook',
    'fb2': 'text/xml',
    'xml': 'text/xml',
}

LANGUAGES_3TO2 = {
    'deu': 'de',
    'ger': 'de',
    'eng': 'en',
    'spa': 'es',
    'fra': 'fr',
    'fre': 'fr',
    'ita': 'it',
    'jpn': 'jp',
    'lit': 'lt',
    'pol': 'pl',
    'rus': 'ru',
    'ukr': 'uk',
}

CATEGORIES_NAME_PLURAL = {
    'author': _('authors'),
    'epoch': _('epochs'),
    'kind': _('kinds'),
    'genre': _('genres'),
    'theme': _('themes'),
    'set': _('sets'),
    'thing': _('things'),
}

WHOLE_CATEGORY = {
    'author': _('All authors'),
    'epoch': _('All epochs'),
    'kind': _('All kinds'),
    'genre': _('All genres'),
    'theme': _('All themes'),
    'set': _('All sets'),
    'thing': _('All things'),
}
