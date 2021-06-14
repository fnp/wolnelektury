from datetime import date, timedelta
from django.core.management.base import BaseCommand
from stats.models import Visits, DayVisits


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-s' ,'--since', metavar='YYYY-MM-DD',
            required=True
        )
        parser.add_argument(
            '-u' ,'--until', metavar='YYYY-MM-DD',
            required=True
        )

        
    def handle(self, **options):
        since = date(*[int(p) for p in options['since'].split('-')])
        until = date(*[int(p) for p in options['until'].split('-')])
        while since < until:
            print(since)
            DayVisits.build_day(since)
            since += timedelta(1)

