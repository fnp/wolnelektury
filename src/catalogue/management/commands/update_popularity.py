# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.core.management.base import BaseCommand
from django.db.models import Count

from catalogue.models import Book, BookPopularity


class Command(BaseCommand):
    help = 'Update popularity counters.'

    def handle(self, **options):
        BookPopularity.objects.all().delete()
        books_with_popularity = Book.objects.filter(tag_relations__tag__category='set').only('id').distinct()\
            .annotate(pop=Count('tag_relations__tag__user', distinct=True))
        pop_list = []
        for book in books_with_popularity:
            pop_list.append(BookPopularity(book=book, count=book.pop))
        books_without_popularity = Book.objects.exclude(tag_relations__tag__category='set')
        for book in books_without_popularity:
            pop_list.append(BookPopularity(book=book, count=0))
        BookPopularity.objects.bulk_create(pop_list, batch_size=512)
