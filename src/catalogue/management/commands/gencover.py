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
        parser.add_argument('--width', type=int)
        parser.add_argument('--height', type=int)
        parser.add_argument('--bleed', action='store_true')
        parser.add_argument('--cover-class', type=str)

    def handle(self, *args, **options):
        slug = options['slug']
        width = options['width']
        height = options.get('height')
        cover_class = options.get('cover_class')
        bleed = 20 if options['bleed'] else 0
        wldoc = Book.objects.get(slug=slug).wldocument()
        kwargs = {}
        if cover_class:
            kwargs['cover_class'] = cover_class
        cover = make_cover(wldoc.book_info, width=width, height=height, bleed=bleed, **kwargs)
        cover.save('%s.jpg' % slug)
