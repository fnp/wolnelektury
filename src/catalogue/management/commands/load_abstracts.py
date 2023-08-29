# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.core.management.base import BaseCommand

from catalogue.models import Book


class Command(BaseCommand):
    def handle(self, *args, **options):
        for b in Book.objects.order_by('slug'):
            print(b.slug)
            b.load_abstract()
            b.save()
