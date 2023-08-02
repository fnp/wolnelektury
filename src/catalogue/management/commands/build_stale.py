# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from time import time
from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.fields import EbookField
from catalogue.models import Book


class Command(BaseCommand):
    help = 'Schedule regenerating stale ebook files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-l', '--limit', type=int,
            help='Limit number of files to build'
        )
        parser.add_argument(
            '-t', '--time', type=int, metavar='SECONDS',
            help='Limit timenumber of files to build'
        )

    def handle(self, **options):
        t = time()
        counter = 0
        while True:
            if options['time'] is not None and time() - t > options['time']:
                break
            if options['limit'] is not None and counter >= options['limit']:
                break
            tasks = EbookField.find_all_stale(Book, 1)
            if not tasks:
                break
            for field_name, book in tasks:
                print(field_name, book)
                try:
                    getattr(book, field_name).build()
                except Exception as e:
                    print('ERROR', e)
