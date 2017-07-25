# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.urlresolvers import reverse
from ssify import flush_ssi_includes
from catalogue.models import Book


class Cite(models.Model):
    book = models.ForeignKey(Book, verbose_name=_('book'), null=True, blank=True)
    text = models.TextField(_('text'), blank=True)
    small = models.BooleanField(_('small'), default=False, help_text=_('Make this cite display smaller.'))
    vip = models.CharField(_('VIP'), max_length=128, null=True, blank=True)
    link = models.URLField(_('link'))
    sticky = models.BooleanField(_('sticky'), default=False, db_index=True,
                                 help_text=_('Sticky cites will take precedense.'))
    banner = models.BooleanField(_('banner'), default=False, help_text=_('Adjust size to image, ignore the text'))

    image = models.ImageField(
        _('image'), upload_to='social/cite', null=True, blank=True,
        help_text=_('Best image is exactly 975px wide and weights under 100kB.'))
    image_shift = models.IntegerField(
        _('shift'), null=True, blank=True,
        help_text=_(u'Vertical shift, in percents. 0 means top, 100 is bottom. Default is 50%.'))
    image_title = models.CharField(_('title'), max_length=255, null=True, blank=True)
    image_author = models.CharField(_('author'), max_length=255, blank=True, null=True)
    image_link = models.URLField(_('link'), blank=True, null=True)
    image_license = models.CharField(_('license name'), max_length=255, blank=True, null=True)
    image_license_link = models.URLField(_('license link'), blank=True, null=True)

    class Meta:
        ordering = ('vip', 'text')
        verbose_name = _('cite')
        verbose_name_plural = _('cites')

    def __unicode__(self):
        return u"%s: %s…" % (self.vip, self.text[:60])

    def get_absolute_url(self):
        """This is used for testing."""
        return "%s?choose_cite=%d" % (reverse('main_page'), self.id)

    def save(self, *args, **kwargs):
        ret = super(Cite, self).save(*args, **kwargs)
        self.flush_includes()
        return ret

    def flush_includes(self):
        flush_ssi_includes([
            template % (self.pk, lang)
            for template in [
                '/ludzie/cite/%s.%s.html',
                '/ludzie/cite_main/%s.%s.html',
            ]
            for lang in [lc for (lc, _ln) in settings.LANGUAGES]] +
            ['/ludzie/cite_info/%s.html' % self.pk])
