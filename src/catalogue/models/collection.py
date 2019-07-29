# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from ssify import flush_ssi_includes
import re


class Collection(models.Model):
    """A collection of books, which might be defined before publishing them."""
    title = models.CharField(_('title'), max_length=120, db_index=True)
    slug = models.SlugField(_('slug'), max_length=120, primary_key=True)
    description = models.TextField(_('description'), null=True, blank=True)
    book_slugs = models.TextField(_('book slugs'))
    kind = models.CharField(_('kind'), max_length=10, blank=False, default='book', db_index=True,
                            choices=(('book', _('book')), ('picture', _('picture'))))

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

    def flush_includes(self, languages=True):
        if not languages:
            return
        if languages is True:
            languages = [lc for (lc, _ln) in settings.LANGUAGES]

        flush_ssi_includes([
            '/katalog/%s.json' % lang for lang in languages])
