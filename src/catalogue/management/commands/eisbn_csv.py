# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import csv
import sys
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime

from catalogue.models import Book
from librarian import RDFNS, DCNS


FORMATS = ('HTML', 'PDF', 'TXT', 'EPUB', 'MOBI')

FORMATS_WITH_CHILDREN = ('PDF', 'EPUB', 'MOBI')


PRODUCT_FORMS_1 = {
    'HTML': 'EC',
    'PDF': 'EB',
    'TXT': 'EB',
    'EPUB': 'ED',
    'MOBI': 'ED',
}

PRODUCT_FORMS_2 = {
    'HTML': 'E105',
    'PDF': 'E107',
    'TXT': 'E112',
    'EPUB': 'E101',
    'MOBI': 'E127',
}

VOLUME_NUMBERS = {
    u'pierwszy': 1,
    u'drugi': 2,
    u'trzeci': 3,
    u'czwarty': 4,
    u'piąty': 5,
    u'szósty': 6,
    u'I': 1,
    u'II': 2,
    u'III': 3,
    u'IV': 4,
    u'V': 5,
    u'VI': 6,
}


def is_institution(name):
    return name.startswith(u'Zgromadzenie Ogólne')


VOLUME_SEPARATOR = ', tom '


def get_volume(title):
    if VOLUME_SEPARATOR not in title:
        return title, ''
    else:
        vol_idx = title.index(VOLUME_SEPARATOR)
        stripped = title[:vol_idx]
        vol_name = title[vol_idx + len(VOLUME_SEPARATOR):]
        if vol_name in VOLUME_NUMBERS:
            return stripped, VOLUME_NUMBERS[vol_name]
        else:
            return title, ''


class Command(BaseCommand):
    @staticmethod
    def dc_values(desc, tag):
        return [e.text for e in desc.findall('.//' + DCNS(tag))]

    def handle(self, *args, **options):
        writer = csv.writer(sys.stdout)
        for book in Book.objects.all():
            desc = book.wldocument().edoc.find('.//' + RDFNS('Description'))
            formats = FORMATS_WITH_CHILDREN if book.children.exists() else FORMATS
            for file_format in formats:
                # imprint = u'Fundacja Nowoczesna Polska'
                imprint = '; '.join(self.dc_values(desc, 'publisher'))
                title, volume = get_volume(book.title)
                subtitle = ''
                year = ''
                publication_date = localtime(book.created_at).date().isoformat()
                info_date = publication_date
                author = '; '.join(self.dc_values(desc, 'creator'))
                author_person = author if not is_institution(author) else ''
                author_institution = author if is_institution(author) else ''
                publication_type = 'DGO'
                edition = '1'
                product_form1 = PRODUCT_FORMS_1[file_format]
                product_form2 = PRODUCT_FORMS_2[file_format]
                language = self.dc_values(desc, 'language')[0]
                row = [
                    imprint,
                    title,
                    subtitle,
                    year,
                    volume,
                    publication_date,
                    info_date,
                    author_person,
                    author_institution,
                    publication_type,
                    edition,
                    product_form1,
                    product_form2,
                    language,
                ]
                writer.writerow([s.encode('utf-8') for s in row])
