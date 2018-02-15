# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import csv
import sys
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime

from catalogue.models import Book
from isbn.utils import isbn_data, FORMATS, FORMATS_WITH_CHILDREN


class Command(BaseCommand):

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
                date = localtime(book.created_at).date().isoformat()
                data = isbn_data(book.wldocument(), file_format)
                row = [
                    data['imprint'],
                    data['title'],
                    data['subtitle'],
                    data['year'],
                    data['part_number'],
                    date,
                    date,
                    data['name'],
                    data['corporate_name'],
                    data['edition_type'],
                    data['edition_number'],
                    data['product_form'],
                    data['product_form_detail'],
                    data['language'],
                    book.slug,
                    file_format,
                ]
                writer.writerow([s.encode('utf-8') for s in row])
