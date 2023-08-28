# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import hashlib

from django.db import models
from django.conf import settings


class Subscription(models.Model):
    email = models.EmailField(verbose_name='adres e-mail', unique=True)
    active = models.BooleanField(default=True, verbose_name='aktywna')
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'subskrypcja'
        verbose_name_plural = 'subskrypcje'

    def __str__(self):
        return self.email

    def hashcode(self):
        return hashlib.sha224(self.email + settings.SECRET_KEY).hexdigest()[:30]


class Newsletter(models.Model):
    slug = models.SlugField(blank=True)
    page_title = models.CharField(max_length=255, blank=True)
    phplist_id = models.IntegerField(null=True, blank=True)
    crm_id = models.IntegerField(null=True, blank=True)
