# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext as _
from datetime import datetime


class Author(models.Model):
    name = models.CharField(_('name'), max_length=50, db_index=True)
    slug = models.SlugField(_('slug'), max_length=120, db_index=True, unique=True)
    sort_key = models.CharField(_('sort key'), max_length=120, db_index=True)
    description = models.TextField(_('description'), blank=True)
    death = models.IntegerField(_(u'year of death'), blank=True, null=True)
    gazeta_link = models.CharField(blank=True, max_length=240)
    wiki_link = models.CharField(blank=True, max_length=240)

    class Meta:
        ordering = ('sort_key',)
        verbose_name = _('author')
        verbose_name_plural = _('authors')

    @property
    def category(self):
        return "author"

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "Author(slug=%r)" % self.slug

    @permalink
    def get_absolute_url(self):
        return ('catalogue.views.tagged_object_list', [self.url_chunk])

    def has_description(self):
        return len(self.description) > 0
    has_description.short_description = _('description')
    has_description.boolean = True

    def alive(self):
        return self.death is None

    def in_pd(self):
        """ tests whether an author is in public domain """
        return self.death is not None and self.goes_to_pd() <= datetime.now().year

    def goes_to_pd(self):
        """ calculates the year of public domain entry for an author """
        return self.death + 71 if self.death is not None else None

    @property
    def url_chunk(self):
        return '/'.join(('autor', self.slug))


class BookStub(models.Model):
    title = models.CharField(_('title'), max_length=120)
    author = models.CharField(_('author'), max_length=120)
    pd = models.IntegerField(_('goes to public domain'), null=True, blank=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True, db_index=True)
    translator = models.TextField(_('translator'), blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = _('book stub')
        verbose_name_plural = _('book stubs')

    def __unicode__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        return ('catalogue.views.book_detail', [self.slug])

    def in_pd(self):
        return self.pd is not None and self.pd <= datetime.now().year

    @property
    def name(self):
        return self.title

