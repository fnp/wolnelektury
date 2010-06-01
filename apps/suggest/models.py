# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Suggestion(models.Model):
    author = models.CharField(_('author'), blank=True, max_length=120)
    email = models.EmailField(_('e-mail'), blank=True)
    title = models.CharField(_('title'), max_length=120)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('creation date'), auto_now=True)
    ip = models.IPAddressField(_('IP address'))
    user = models.ForeignKey(User, blank=True, null=True)
    
    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('suggestion')
        verbose_name_plural = _('suggestions')
    
    def __unicode__(self):
        return self.title
    