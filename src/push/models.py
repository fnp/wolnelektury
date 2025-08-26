# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import models


class Notification(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=256, verbose_name='tytuł')
    body = models.CharField(max_length=2048, verbose_name='treść')
    image = models.ImageField(verbose_name='obraz', blank=True, upload_to='push/img')
    message_id = models.CharField(max_length=2048)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return '%s: %s' % (self.timestamp, self.title)


class DeviceToken(models.Model):
    user = models.ForeignKey('auth.User', models.CASCADE)
    token = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at',)
