# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class Chunk(models.Model):
    """
    A Chunk is a piece of content associated with a unique key that can be inserted into
    any template with the use of a special template tag.
    """
    key = models.CharField(_('key'), help_text=_('A unique name for this chunk of content'), primary_key=True,
                           max_length=255)
    description = models.CharField(_('description'), blank=True, max_length=255)
    content = models.TextField(_('content'), blank=True)

    class Meta:
        ordering = ('key',)
        verbose_name = _('chunk')
        verbose_name_plural = _('chunks')

    def __str__(self):
        return self.key

    def save(self, *args, **kwargs):
        ret = super(Chunk, self).save(*args, **kwargs)
        for lc, ln in settings.LANGUAGES:
            cache.delete('chunk:%s:%s' % (self.key, lc))
        return ret


class Attachment(models.Model):
    key = models.CharField(_('key'), help_text=_('A unique name for this attachment'), primary_key=True, max_length=255)
    attachment = models.FileField(upload_to='chunks/attachment')

    class Meta:
        ordering = ('key',)
        verbose_name, verbose_name_plural = _('attachment'), _('attachments')

    def __str__(self):
        return self.key

    def get_absolute_url(self):
        return reverse('chunks_attachment', args=[self.key, self.attachment.name.rsplit('.', 1)[-1]])


class Menu(models.Model):
    identifier = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.identifier


class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, models.CASCADE)
    order = models.SmallIntegerField()
    highlight = models.BooleanField()
    infopage = models.ForeignKey(
        'infopages.InfoPage', models.PROTECT, null=True, blank=True)
    url = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ('order',)

    @property
    def final_name(self):
        if self.name == '-':
            return mark_safe('<hr>')
        if self.name:
            return self.name
        if self.infopage:
            return self.infopage.title
        return ''

    @property
    def final_link(self):
        if self.infopage:
            return self.infopage.get_absolute_url()
        return self.url

    @property
    def has_link(self):
        return self.url or self.infopage
