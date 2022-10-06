# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from newtagging import managers
from catalogue.models import Tag
from wolnelektury.utils import cached_render, clear_cached_renders


class Fragment(models.Model):
    """Represents a themed fragment of a book."""
    text = models.TextField()
    short_text = models.TextField(editable=False)
    anchor = models.CharField(max_length=120)
    book = models.ForeignKey('Book', models.CASCADE, related_name='fragments')

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(Tag)
    tags = managers.TagDescriptor(Tag)
    tag_relations = GenericRelation(Tag.intermediary_table_model)

    class Meta:
        ordering = ('book', 'anchor',)
        verbose_name = _('fragment')
        verbose_name_plural = _('fragments')
        app_label = 'catalogue'

    def get_absolute_url(self):
        return '%s#m%s' % (reverse('book_text', args=[self.book.slug]), self.anchor)

    def get_api_url(self):
        return reverse('catalogue_api_fragment', args=[self.book.slug, self.anchor])

    def get_short_text(self):
        """Returns short version of the fragment."""
        return self.short_text if self.short_text else self.text

    @cached_render('catalogue/fragment_short.html')
    def midi_box(self):
        return {'fragment': self}

    @cached_render('catalogue/fragment_promo.html')
    def promo_box(self):
        return {'fragment': self}

    @property
    def themes(self):
        return self.tags.filter(category='theme')

    def clear_cache(self):
        clear_cached_renders(self.midi_box)
        clear_cached_renders(self.promo_box)
