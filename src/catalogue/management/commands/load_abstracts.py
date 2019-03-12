# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.management.base import BaseCommand

from catalogue.models import Book


class Command(BaseCommand):
    def handle(self, *args, **options):
        for b in Book.objects.order_by('slug'):
            print(b.slug)
            b.load_abstract()
            b.save()
