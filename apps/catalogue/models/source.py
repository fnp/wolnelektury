# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Source(models.Model):
    """A collection of books, which might be defined before publishing them."""
    netloc = models.CharField(_('network location'), max_length=120, primary_key=True)
    name = models.CharField(_('name'), max_length=120)

    class Meta:
        ordering = ('netloc',)
        verbose_name = _('source')
        verbose_name_plural = _('sources')
        app_label = 'catalogue'

    def __unicode__(self):
        return self.netloc
