# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import timedelta
import traceback
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from club.models import PayUOrder
from funding.models import Funding
from paypal.models import BillingAgreement


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'year', type=int, metavar='YEAR',
            help='Send receipts for the year.')
        parser.add_argument(
            '--emails',
            help='Send only to these emails.')

    def handle(self, *args, **options):
        year = options['year']
        emails = set(
            PayUOrder.objects.filter(
                completed_at__year=year
            ).order_by('schedule__email').values_list(
                'schedule__email', flat=True
            ).distinct()
        )
        emails.update(
            BillingAgreement.objects.all().order_by(
                'schedule__email').values_list(
                'schedule__email', flat=True
            ).distinct()
        )
        emails.update(
            Funding.objects.exclude(email='').filter(
                payed_at__year=year
            ).order_by('email').values_list(
                'email', flat=True
            ).distinct()
        )

        if options['emails']:
            emails = options['emails'].split(',')

        for email in emails:
            print(email)
            try:
                PayUOrder.send_receipt(email, year)
            except:
                print('ERROR')
