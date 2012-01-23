# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _

from catalogue.models import Book


class Cite(models.Model):
    book = models.ForeignKey(Book)
    text = models.TextField(_('text'))
    vip = models.CharField(_('VIP'), max_length=128, null=True, blank=True)
    link = models.URLField(_('link'))

    def get_absolute_url(self):
        return self.link
