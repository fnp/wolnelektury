# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.apps import apps
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.db.models.signals import post_save, post_delete
from search.utils import UnaccentSearchVector


class Author(models.Model):
    name = models.CharField(_('name'), max_length=50, db_index=True)
    slug = models.SlugField(_('slug'), max_length=120, db_index=True, unique=True)
    sort_key = models.CharField(_('sort key'), max_length=120, db_index=True)
    description = models.TextField(_('description'), blank=True)
    death = models.IntegerField(_('year of death'), blank=True, null=True)
    gazeta_link = models.CharField(blank=True, max_length=240)
    wiki_link = models.CharField(blank=True, max_length=240)

    class Meta:
        ordering = ('sort_key',)
        verbose_name = _('author')
        verbose_name_plural = _('authors')

    @property
    def category(self):
        return "author"

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Author(slug=%r)" % self.slug

    def get_absolute_url(self):
        return reverse('tagged_object_list', args=[self.url_chunk])

    def has_description(self):
        return len(self.description) > 0
    has_description.short_description = _('description')
    has_description.boolean = True

    @classmethod
    def search(cls, query, qs=None):
        Tag = apps.get_model('catalogue', 'Tag')
        if qs is None:
            qs = cls.objects.all()
        pd_authors = qs.annotate(search_vector=UnaccentSearchVector('name')).filter(search_vector=query)
        existing_slugs = Tag.objects.filter(
            category='author', slug__in=list(pd_authors.values_list('slug', flat=True))) \
            .values_list('slug', flat=True)
        pd_authors = pd_authors.exclude(slug__in=existing_slugs)
        return pd_authors

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

    def __str__(self):
        return self.title

    @classmethod
    def search(cls, query, qs=None):
        Book = apps.get_model('catalogue', 'Book')
        if qs is None:
            qs = cls.objects.all()
        pd_books = qs.annotate(search_vector=UnaccentSearchVector('title')).filter(search_vector=query)
        existing_slugs = Book.objects.filter(
            slug__in=list(pd_books.values_list('slug', flat=True))) \
            .values_list('slug', flat=True)
        pd_books = pd_books.exclude(slug__in=existing_slugs)
        return pd_books

    def get_absolute_url(self):
        return reverse('book_detail', args=[self.slug])

    def in_pd(self):
        return self.pd is not None and self.pd <= datetime.now().year

    @property
    def name(self):
        return self.title

    def pretty_title(self, html_links=False):
        return ', '.join((self.author, self.title))


if not settings.NO_SEARCH_INDEX:
    def update_index(sender, instance, **kwargs):
        from search.index import Index
        idx = Index()
        idx.index_tags(instance, remove_only='created' not in kwargs)

    post_delete.connect(update_index, Author)
    post_delete.connect(update_index, BookStub)
    post_save.connect(update_index, Author)
    post_save.connect(update_index, BookStub)
