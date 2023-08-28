# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.urls import reverse


class Catalog(models.Model):
    """Represents a dictionary of libraries"""

    name = models.CharField('nazwa', max_length=120, null=False)
    slug = models.SlugField('slug', max_length=120, unique=True, db_index=True)

    class Meta:
        verbose_name = 'katalog'
        verbose_name_plural = 'katalogi'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('libraries_catalog_view', args=[self.slug])


class Library(models.Model):
    """Represent a single library in the libraries dictionary"""

    name = models.CharField('nazwa', max_length=120, blank=True)
    slug = models.SlugField('slug', max_length=120, unique=True, db_index=True, null=True)
    catalog = models.ForeignKey(Catalog, null=False, related_name='libraries', on_delete=models.PROTECT)
    url = models.CharField('url', max_length=120, blank=True)
    description = models.TextField('opis', blank=True)

    class Meta:
        verbose_name = 'biblioteka'
        verbose_name_plural = 'biblioteki'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('libraries_library_view', args=[self.catalog.slug, self.slug])
