# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import print_function, unicode_literals

from django.core.management.base import BaseCommand
from django.db.models import Count

from catalogue.models import Book, BookPopularity


class Command(BaseCommand):
    help = 'Update popularity counters.'

    def handle(self, **options):
        BookPopularity.objects.all().delete()
        books_with_popularity = Book.objects.filter(tag_relations__tag__category='set').only('id').distinct()\
            .annotate(pop=Count('tag_relations__tag__user', distinct=True))
        for book in books_with_popularity:
            BookPopularity.objects.create(book=book, count=book.pop)
        books_without_popularity = Book.objects.exclude(tag_relations__tag__category='set')
        for book in books_without_popularity:
            BookPopularity.objects.create(book=book, count=0)
