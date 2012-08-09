# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.core.cache import get_cache
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, ugettext_lazy as _
from newtagging import managers
from catalogue.models import Tag


permanent_cache = get_cache('permanent')


class Fragment(models.Model):
    """Represents a themed fragment of a book."""
    text = models.TextField()
    short_text = models.TextField(editable=False)
    anchor = models.CharField(max_length=120)
    book = models.ForeignKey('Book', related_name='fragments')

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(Tag)
    tags = managers.TagDescriptor(Tag)

    class Meta:
        ordering = ('book', 'anchor',)
        verbose_name = _('fragment')
        verbose_name_plural = _('fragments')
        app_label = 'catalogue'

    def get_absolute_url(self):
        return '%s#m%s' % (reverse('book_text', args=[self.book.slug]), self.anchor)

    def reset_short_html(self):
        if self.id is None:
            return

        cache_key = "Fragment.short_html/%d/%s"
        for lang, langname in settings.LANGUAGES:
            permanent_cache.delete(cache_key % (self.id, lang))

    def get_short_text(self):
        """Returns short version of the fragment."""
        return self.short_text if self.short_text else self.text

    def short_html(self):
        if self.id:
            cache_key = "Fragment.short_html/%d/%s" % (self.id, get_language())
            short_html = permanent_cache.get(cache_key)
        else:
            short_html = None

        if short_html is not None:
            return mark_safe(short_html)
        else:
            short_html = unicode(render_to_string('catalogue/fragment_short.html',
                {'fragment': self}))
            if self.id:
                permanent_cache.set(cache_key, short_html)
            return mark_safe(short_html)
