# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import timedelta
import traceback
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from club.models import PayUOrder


class Command(BaseCommand):
    def handle(self, *args, **options):
        year = 2019
        skipping = True
        for email in PayUOrder.objects.filter(completed_at__year=2019).order_by('schedule__email').values_list('schedule__email', flat=True).distinct():
            #if email !='rczajka@rczajka.pl': continue
            if email == 'agnieszka_karcz@op.pl': skipping=False
            if skipping:
                continue
            print(email)
            PayUOrder.send_receipt(email, year)
