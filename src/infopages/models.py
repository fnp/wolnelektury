# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _


class InfoPage(models.Model):
    """An InfoPage is used to display a two-column flatpage."""

    main_page = models.IntegerField(_('main page priority'), null=True, blank=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True, db_index=True)
    title = models.CharField(_('title'), max_length=120, blank=True)
    left_column = models.TextField(_('left column'), blank=True)
    right_column = models.TextField(_('right column'), blank=True)

    class Meta:
        ordering = ('main_page', 'slug',)
        verbose_name = _('info page')
        verbose_name_plural = _('info pages')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return 'infopage', [self.slug]
