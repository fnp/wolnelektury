# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import re
from wolnelektury.utils import cached_render, clear_cached_renders


class Collection(models.Model):
    """A collection of books, which might be defined before publishing them."""
    title = models.CharField(_('title'), max_length=120, db_index=True)
    slug = models.SlugField(_('slug'), max_length=120, primary_key=True)
    description = models.TextField(_('description'), blank=True)
    book_slugs = models.TextField(_('book slugs'))
    authors = models.ManyToManyField(
        'Tag',
        limit_choices_to={'category': 'author'},
        blank=True
    )
    kind = models.CharField(_('kind'), max_length=10, blank=False, default='book', db_index=True,
                            choices=(('book', _('book')), ('picture', _('picture'))))
    listed = models.BooleanField(_('listed'), default=True, db_index=True)
    role = models.CharField(max_length=128, blank=True, db_index=True, choices=[
        ('', '–'),
        ('recommend', _('recommended')),
    ])

    class Meta:
        ordering = ('title',)
        verbose_name = _('collection')
        verbose_name_plural = _('collections')
        app_label = 'catalogue'

    def __str__(self):
        return self.title

    def get_initial(self):
        try:
            return re.search(r'\w', self.title, re.U).group(0)
        except AttributeError:
            return ''

    def get_absolute_url(self):
        return reverse("collection", args=[self.slug])

    def get_query(self):
        slugs = self.book_slugs.split()
        # allow URIs
        slugs = [slug.rstrip('/').rsplit('/', 1)[-1] if '/' in slug else slug for slug in slugs]
        return models.Q(slug__in=slugs)

    def get_books(self):
        from catalogue.models import Book
        return Book.objects.filter(self.get_query())

    def get_5_books(self):
        return self.get_books()[:5]

    @cached_render('catalogue/collection_box.html')
    def box(self):
        return {
            'collection': self
        }

    def clear_cache(self):
        clear_cached_renders(self.box)
