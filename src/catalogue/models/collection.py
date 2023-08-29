# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings
from django.db import models
from django.urls import reverse
import re
from wolnelektury.utils import cached_render, clear_cached_renders


class Collection(models.Model):
    """A collection of books, which might be defined before publishing them."""
    title = models.CharField('tytuł', max_length=120, db_index=True)
    slug = models.SlugField('slug', max_length=120, primary_key=True)
    description = models.TextField('opis', blank=True)
    book_slugs = models.TextField('slugi książek')
    authors = models.ManyToManyField(
        'Tag',
        limit_choices_to={'category': 'author'},
        blank=True
    )
    kind = models.CharField('rodzaj', max_length=10, blank=False, default='book', db_index=True,
                            choices=(('book', 'książki'), ('picture', 'obrazy')))
    listed = models.BooleanField('na liście', default=True, db_index=True)
    role = models.CharField(max_length=128, blank=True, db_index=True, choices=[
        ('', '–'),
        ('recommend', 'polecane'),
    ])

    class Meta:
        ordering = ('title',)
        verbose_name = 'kolekcja'
        verbose_name_plural = 'kolekcje'
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

    def example3(self):
        return self.get_books()[:3]

    def clear_cache(self):
        clear_cached_renders(self.box)
