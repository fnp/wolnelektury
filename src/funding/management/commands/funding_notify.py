# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sends relevant funding notifications.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-q', '--quiet', action='store_false', dest='verbose',
            default=True, help='Suppress output')

    def handle(self, **options):

        from datetime import date, timedelta
        from funding.models import Offer
        from funding import app_settings
        from django.core.cache import caches
        from django.conf import settings

        verbose = options['verbose']

        for offer in Offer.past().filter(notified_end=None):
            if verbose:
                print('Notify end:', offer)
            # The 'WL fund' list needs to be updated.
            caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
            offer.flush_includes()
            offer.notify_end()

        current = Offer.current()
        if (current is not None and
                current.end <= date.today() + timedelta(app_settings.DAYS_NEAR - 1) and
                not current.notified_near):
            if verbose:
                print('Notify near:', current)
            current.notify_near()
