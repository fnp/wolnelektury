# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Notification(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=256, verbose_name=_('title'))
    body = models.CharField(max_length=2048, verbose_name=_('content'))
    image = models.ImageField(verbose_name=_('image'), blank=True, upload_to='push/img')
    message_id = models.CharField(max_length=2048)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return '%s: %s' % (self.timestamp, self.title)
