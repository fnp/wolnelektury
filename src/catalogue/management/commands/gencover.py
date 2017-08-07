# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.management.base import BaseCommand

from catalogue.models import Book
from librarian.cover import make_cover


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('slug')
        parser.add_argument('size', type=int)
        parser.add_argument('--bleed', action='store_true')

    def handle(self, *args, **options):
        slug = options['slug']
        size = options['size']
        bleed = 20 if options['bleed'] else 0
        wldoc = Book.objects.get(slug=slug).wldocument()
        cover = make_cover(wldoc.book_info, width=size, bleed=bleed)
        cover.save('%s.jpg' % slug)
