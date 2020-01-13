# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import timedelta
import traceback
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from club.models import Schedule


class Command(BaseCommand):
    def handle(self, *args, **options):
        for s in Schedule.objects.exclude(monthly=False, yearly=False).filter(is_cancelled=False, expires_at__lt=now() + timedelta(1)):
            print(s, s.email, s.expires_at)
            try:
                s.pay(None)
            except:
                traceback.print_exc()


