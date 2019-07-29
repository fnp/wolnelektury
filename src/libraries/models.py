# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class Catalog(models.Model):
    """Represents a dictionary of libraries"""

    name = models.CharField(_('name'), max_length=120, null=False)
    slug = models.SlugField(_('slug'), max_length=120, unique=True, db_index=True)

    class Meta:
        verbose_name = _('catalog')
        verbose_name_plural = _('catalogs')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('libraries_catalog_view', args=[self.slug])


class Library(models.Model):
    """Represent a single library in the libraries dictionary"""

    name = models.CharField(_('name'), max_length=120, blank=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True, db_index=True, null=True)
    catalog = models.ForeignKey(Catalog, null=False, related_name='libraries', on_delete=models.PROTECT)
    url = models.CharField(_('url'), max_length=120, blank=True)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        verbose_name = _('library')
        verbose_name_plural = _('libraries')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('libraries_library_view', args=[self.catalog.slug, self.slug])
