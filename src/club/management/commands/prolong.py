from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from club.models import Schedule


class Command(BaseCommand):
    def handle(self, *args, **options):
        for s in Schedule.objects.filter(is_cancelled=False, expires_at__lt=now() + timedelta(1)):
            print(s, s.email, s.expires_at)
            s.pay(None)

