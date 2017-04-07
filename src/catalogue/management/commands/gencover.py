# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.management.base import BaseCommand

from catalogue.models import Book
from librarian.cover import DefaultEbookCover


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('slug')
        parser.add_argument('size', type=int)

    def handle(self, *args, **options):
        slug = options['slug']
        size = options['size']
        wldoc = Book.objects.get(slug=slug).wldocument()
        cover = DefaultEbookCover(wldoc.book_info, width=size)
        cover.save('%s.jpg' % slug)
