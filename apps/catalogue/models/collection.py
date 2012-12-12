# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Collection(models.Model):
    """A collection of books, which might be defined before publishing them."""
    title = models.CharField(_('title'), max_length=120, db_index=True)
    slug = models.SlugField(_('slug'), max_length=120, primary_key=True)
    description = models.TextField(_('description'), null=True, blank=True)

    models.SlugField(_('slug'), max_length=120, unique=True, db_index=True)
    book_slugs = models.TextField(_('book slugs'))

    class Meta:
        ordering = ('title',)
        verbose_name = _('collection')
        verbose_name_plural = _('collections')
        app_label = 'catalogue'

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ("collection", [self.slug])
