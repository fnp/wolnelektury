# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import re
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User


class Suggestion(models.Model):
    contact = models.CharField('kontakt', blank=True, max_length=120)
    description = models.TextField('opis', blank=True)
    created_at = models.DateTimeField('data utworzenia', auto_now=True)
    ip = models.GenericIPAddressField('adres IP')
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'sugestia'
        verbose_name_plural = 'sugestie'

    def __str__(self):
        return str(self.created_at)


class PublishingSuggestion(models.Model):
    contact = models.CharField('kontakt', blank=True, max_length=120)
    books = models.TextField('książki', null=True, blank=True)
    audiobooks = models.TextField('audiobooki', null=True, blank=True)
    created_at = models.DateTimeField('data utworzenia', auto_now_add=True)
    ip = models.GenericIPAddressField('adres IP')
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'sugestia publikacji'
        verbose_name_plural = 'sugestie publikacji'

    def is_spam(self):
        suggestion_text = (self.books or self.audiobooks).strip(' \r\n,')
        # similar = PublishingSuggestion.objects.filter(
        #     books__in=('', suggestion_text), audiobooks__in=('', suggestion_text))
        similar = PublishingSuggestion.objects.filter(books=self.books, audiobooks=self.audiobooks).exclude(pk=self.pk)
        http = 'http' in suggestion_text
        spam = False
        if re.search(r'([^\W\d_])\1\1\1', suggestion_text):
            # same letter repetition outside URL
            spam = True
        elif re.search(r'[^\W\d_]\d|\d[^\W\d_]', suggestion_text) and not http:
            # string of letters and digits outside URL
            spam = True
        elif re.search(r'[^\W\d_]{17}', suggestion_text):
            # long string of letters (usually gibberish)
            spam = True
        elif ' ' not in suggestion_text:
            # single word - usually spam
            spam = True
        elif len(suggestion_text) < 11:
            # too short
            spam = True
        elif similar.filter(created_at__range=(self.created_at - timedelta(1), self.created_at)):
            # the same suggestion within 24h
            spam = True
        elif similar.filter(ip=self.ip):
            # the same suggestion from the same IP
            spam = True
        return spam

    def __str__(self):
        return str(self.created_at)
