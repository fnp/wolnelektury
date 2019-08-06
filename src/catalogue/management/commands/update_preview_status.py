# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import date
from django.core.management.base import BaseCommand

from catalogue.models import Book


class Command(BaseCommand):
    def handle(self, *args, **options):
        for book in Book.objects.filter(preview=True, preview_until__lt=date.today()):
            book.preview = False
            book.save()
            for format_ in Book.formats:
                media_file = book.get_media(format_)
                if media_file:
                    media_file.set_readable(True)
