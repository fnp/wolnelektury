# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from newtagging import managers
from catalogue.models import Tag
from ssify import flush_ssi_includes


class Fragment(models.Model):
    """Represents a themed fragment of a book."""
    text = models.TextField()
    short_text = models.TextField(editable=False)
    anchor = models.CharField(max_length=120)
    book = models.ForeignKey('Book', related_name='fragments')

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(Tag)
    tags = managers.TagDescriptor(Tag)
    tag_relations = GenericRelation(Tag.intermediary_table_model)

    short_html_url_name = 'catalogue_fragment_short'

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

    @property
    def themes(self):
        return self.tags.filter(category='theme')

    def flush_includes(self, languages=True):
        if not languages:
            return
        if languages is True:
            languages = [lc for (lc, _ln) in settings.LANGUAGES]
        flush_ssi_includes([
            template % (self.pk, lang)
            for template in [
                '/katalog/f/%d/short.%s.html',
                '/api/include/fragment/%d.%s.json',
                '/api/include/fragment/%d.%s.xml',
                ]
            for lang in languages
            ])
