# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import models
from django.urls import reverse


class InfoPage(models.Model):
    """An InfoPage is used to display a two-column flatpage."""

    slug = models.SlugField('slug', max_length=120, unique=True, db_index=True)
    title = models.CharField('tytuł', max_length=120, blank=True)
    left_column = models.TextField('lewa kolumna', blank=True)
    right_column = models.TextField('prawa kolumna', blank=True)

    class Meta:
        verbose_name = 'strona informacyjna'
        verbose_name_plural = 'strony informacyjne'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('infopage', args=[self.slug])
