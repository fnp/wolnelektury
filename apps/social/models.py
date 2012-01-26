# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from catalogue.models import Book


class Cite(models.Model):
    book = models.ForeignKey(Book)
    text = models.TextField(_('text'))
    small = models.BooleanField(_('small'), default=False, help_text=_('Make this cite display smaller.'))
    vip = models.CharField(_('VIP'), max_length=128, null=True, blank=True)
    link = models.URLField(_('link'))

    class Meta:
        ordering = ('vip', 'text')

    def __unicode__(self):
        return u"%s: %s…" % (self.vip, self.text[:60])

    def get_absolute_url(self):
        """This is used for testing."""
        return "%s?choose_cite=%d" % (reverse('main_page'), self.id)
