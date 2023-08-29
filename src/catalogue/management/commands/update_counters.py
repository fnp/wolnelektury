# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.helpers import update_counters
from wolnelektury.utils import makedirs


class Command(BaseCommand):
    help = 'Update counters.'

    def handle(self, **options):
        makedirs(settings.VAR_DIR)
        update_counters()
