# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _

from os import path

class Document(models.Model):
    """Document - hand-out for teachers"""
    title = models.CharField(_('title'), max_length=120)
    slug = models.SlugField(_('slug'))
    file = models.FileField(_('file'), upload_to='lessons/document')
    author = models.CharField(_('author'), blank=True, max_length=120)
    slideshare_id = models.CharField(_('slideshare ID'), blank=True, max_length=120)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    html = models.TextField(_('HTML'), blank=True) # HTML content, alternative for Flash

    def slideshare_player(self):
        base, ext = path.splitext(self.file.name)
        if ext in ('.ppt', '.pps', '.pot', '.pptx', '.potx', '.ppsx', '.odp', '.key', '.zip', '.pdf',):
            return 'ssplayer2.swf'
        else:
            return 'ssplayerd.swf'

    class Meta:
        ordering = ['slug']
        verbose_name, verbose_name_plural = _("document"), _("documents")

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('lessons_document_detail', [self.slug])
