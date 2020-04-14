# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.fields import EbookField


class Command(BaseCommand):
    help = 'Schedule regenerating stale ebook files.'

    def handle(self, **options):
        EbookField.schedule_all_stale()
