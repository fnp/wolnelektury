# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.utils.translation import ugettext_lazy as _

LICENSES = {
    'http://creativecommons.org/licenses/by-sa/3.0/': {
        'icon': 'cc-by-sa',
        'description': _('Creative Commons Attribution-ShareAlike 3.0 Unported'),
    },
}

# Those will be generated only for books with own HTML.
EBOOK_FORMATS_WITHOUT_CHILDREN = ['txt', 'fb2']
# Those will be generated for all books.
EBOOK_FORMATS_WITH_CHILDREN = ['pdf', 'epub', 'mobi']
# Those will be generated when inherited cover changes.
EBOOK_FORMATS_WITH_COVERS = ['pdf', 'epub', 'mobi']

EBOOK_FORMATS = EBOOK_FORMATS_WITHOUT_CHILDREN + EBOOK_FORMATS_WITH_CHILDREN
