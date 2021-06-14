import re
from urllib.request import urlopen
from django.apps import apps
from django.conf import settings
from django.db import models


class VisitsBase(models.Model):
    book = models.ForeignKey('catalogue.Book', models.CASCADE)
    date = models.DateField()
    views = models.IntegerField()
    unique_views = models.IntegerField()

    class Meta:
        abstract = True

    @classmethod
    def build_for_date(cls, date, period):
        Book = apps.get_model('catalogue', 'Book')

        date = date.isoformat()
        url = f'{settings.PIWIK_URL}?date={date}&filter_limit=-1&format=CSV&idSite={settings.PIWIK_SITE_ID}&language=pl&method=Actions.getPageUrls&module=API&period={period}&segment=&token_auth={settings.PIWIK_TOKEN}&flat=1'
        data = urlopen(url).read().decode('utf-16')
        lines = data.split('\n')[1:]
        for line in lines:
            m = re.match('^/katalog/lektura/([^,]+)\.html,', line)
            if m is not None:
                slug = m.group(1)
                _url, uviews, views, _rest = line.split(',', 3)
                uviews = int(uviews)
                views = int(views)
                try:
                    book = Book.objects.get(slug=slug)
                except Book.DoesNotExist:
                    continue
                else:
                    cls.objects.update_or_create(
                        book=book, date=date,
                        defaults={'views': views, 'unique_views': uviews}
                    )


class Visits(VisitsBase):
    @classmethod
    def build_month(cls, date):
        cls.build_for_date(date.replace(day=1), 'month')


class DayVisits(VisitsBase):
    @classmethod
    def build_day(cls, date):
        cls.build_for_date(date, 'day')

