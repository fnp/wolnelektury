# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from librarian import RDFNS, DCNS


FORMATS = ('PDF', 'HTML', 'TXT', 'EPUB', 'MOBI')

FORMATS_WITH_CHILDREN = ('PDF', 'EPUB', 'MOBI')

PRODUCT_FORMS = {
    'HTML': 'EC',
    'PDF': 'EB',
    'TXT': 'EB',
    'EPUB': 'ED',
    'MOBI': 'ED',
    'SOFT': 'BC',
}

PRODUCT_FORM_DETAILS = {
    'HTML': 'E105',
    'PDF': 'E107',
    'TXT': 'E112',
    'EPUB': 'E101',
    'MOBI': 'E127',
}

PRODUCT_FORMATS = {
    'E105': ('html', 'text/html'),
    'E107': ('pdf', 'application/pdf'),
    'E112': ('txt', 'text/plain'),
    'E101': ('epub', 'application/epub+zip'),
    'E127': ('mobi', 'application/x-mobipocket-ebook'),
}

VOLUME_SEPARATORS = ('. część ', ', część ', ', tom ', '. der tragödie ')


def is_institution(name):
    return name.startswith('Zgromadzenie Ogólne')


def get_volume(title):
    for volume_separator in VOLUME_SEPARATORS:
        if volume_separator in title.lower():
            vol_idx = title.lower().index(volume_separator)
            stripped = title[:vol_idx]
            vol_name = title[vol_idx + 2:]
            return stripped, vol_name
    return title, ''


def dc_values(desc, tag):
    return [e.text.strip() for e in desc.findall('.//' + DCNS(tag))]


def isbn_data(wldoc, file_format=None):
    desc = wldoc.edoc.find('.//' + RDFNS('Description'))
    title, volume = get_volume(dc_values(desc, 'title')[0])
    author = '; '.join(author.strip() for author in dc_values(desc, 'creator'))
    data = {
        'imprint': '; '.join(dc_values(desc, 'publisher')),
        'title': title,
        'subtitle': '',
        'year': '',
        'part_number': volume,
        'name': author if not is_institution(author) else '',
        'corporate_name': author if is_institution(author) else '',
        'edition_type': 'DGO',
        'edition_number': '1',
        'language': dc_values(desc, 'language')[0],
        'dc_slug': wldoc.book_info.url.slug,
    }
    if file_format:
        data['product_form'] = PRODUCT_FORMS[file_format]
        data['product_form_detail'] = PRODUCT_FORM_DETAILS[file_format]
        return data
    else:
        has_children = len(dc_values(desc, 'relation.hasPart')) > 0
        data['formats'] = FORMATS_WITH_CHILDREN if has_children else FORMATS
        return data
