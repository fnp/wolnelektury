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


FORMATS = ('PDF', 'HTML', 'TXT', 'EPUB', 'MOBI')

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


def is_institution(name):
    return name.startswith(u'Zgromadzenie Ogólne')


VOLUME_SEPARATORS = (u'. część ', u', część ', u', tom ', u'. der tragödie ')


def get_volume(title):
    for volume_separator in VOLUME_SEPARATORS:
        if volume_separator in title.lower():
            vol_idx = title.lower().index(volume_separator)
            stripped = title[:vol_idx]
            vol_name = title[vol_idx + 2:]
            return stripped, vol_name
    return title, ''


class Command(BaseCommand):
    @staticmethod
    def dc_values(desc, tag):
        return [e.text for e in desc.findall('.//' + DCNS(tag))]

    def handle(self, *args, **options):
        slugs = [line.strip() for line in sys.stdin]
        writer = csv.writer(sys.stdout)
        all_books = Book.objects.filter(slug__in=slugs)
        books_without_children = all_books.filter(children=None)
        for file_format in FORMATS:
            if file_format in FORMATS_WITH_CHILDREN:
                books = all_books
            else:
                books = books_without_children
            for book in books:
                desc = book.wldocument().edoc.find('.//' + RDFNS('Description'))
                imprint = '; '.join(self.dc_values(desc, 'publisher'))
                title, volume = get_volume(book.title)
                subtitle = ''
                year = ''
                publication_date = localtime(book.created_at).date().isoformat()
                info_date = publication_date
                author = '; '.join(author.strip() for author in self.dc_values(desc, 'creator'))
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
                    book.slug,
                    file_format,
                ]
                writer.writerow([s.encode('utf-8') for s in row])
