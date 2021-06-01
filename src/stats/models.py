import re
from urllib.request import urlopen
from django.apps import apps
from django.conf import settings
from django.db import models


class Visits(models.Model):
    book = models.ForeignKey('catalogue.Book', models.CASCADE)
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    views = models.IntegerField()
    unique_views = models.IntegerField()

    @classmethod
    def build_month(cls, year, month):
        Book = apps.get_model('catalogue', 'Book')
        ### TODO: Delete existing?

        date = f'{year}-{month:02d}'
        url = f'{settings.PIWIK_URL}?date={date}&filter_limit=-1&format=CSV&idSite={settings.PIWIK_SITE_ID}&language=pl&method=Actions.getPageUrls&module=API&period=month&segment=&token_auth={settings.PIWIK_TOKEN}&flat=1'
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
                    cls.objects.create(
                        book=book, year=year, month=month,
                        views=views, unique_views=uviews
                    )
