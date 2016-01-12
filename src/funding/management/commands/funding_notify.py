# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from optparse import make_option
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_false', dest='verbose', default=True, help='Suppress output'),
    )
    help = 'Sends relevant funding notifications.'

    def handle(self, **options):

        from datetime import date, timedelta
        from funding.models import Offer
        from funding import app_settings
        from django.core.cache import caches
        from django.conf import settings

        verbose = options['verbose']

        for offer in Offer.past().filter(notified_end=None):
            if verbose:
                print 'Notify end:', offer
            # The 'WL fund' list needs to be updated.
            caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
            offer.flush_includes()
            offer.notify_end()

        current = Offer.current()
        if (current is not None and
                current.end <= date.today() + timedelta(app_settings.DAYS_NEAR - 1) and
                not current.notified_near):
            if verbose:
                print 'Notify near:', current
            current.notify_near()
