# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
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
        tasks = []
        while True:
            if options['time'] is not None and time() - t > options['time']:
                break
            if options['limit'] is not None and counter >= options['limit']:
                break
            if not tasks:
                tasks = EbookField.find_all_stale(Book, options['limit'] or 100)
            if not tasks:
                break
            field_name, book = tasks.pop(0)
            print(field_name, book)
            counter += 1
            try:
                getattr(book, field_name).build()
            except Exception as e:
                print('ERROR', e)
