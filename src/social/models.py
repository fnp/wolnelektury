# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from random import randint
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, get_language
from catalogue.models import Book
from wolnelektury.utils import cached_render, clear_cached_renders


class BannerGroup(models.Model):
    name = models.CharField(_('name'), max_length=255, unique=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('banner group')
        verbose_name_plural = _('banner groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """This is used for testing."""
        return "%s?banner_group=%d" % (reverse('main_page'), self.id)

    def get_banner(self):
        banners = self.cite_set.all()
        count = banners.count()
        if not count:
            return None
        return banners[randint(0, count-1)]


class Cite(models.Model):
    book = models.ForeignKey(Book, models.CASCADE, verbose_name=_('book'), null=True, blank=True)
    text = models.TextField(_('text'), blank=True)
    small = models.BooleanField(_('small'), default=False, help_text=_('Make this cite display smaller.'))
    vip = models.CharField(_('VIP'), max_length=128, null=True, blank=True)
    link = models.URLField(_('link'))
    video = models.URLField(_('video'), blank=True)
    picture = models.ImageField(_('picture'), blank=True,
            help_text='Najlepsze wymiary: 975 x 315 z tekstem, 487 x 315 bez tekstu.')
    picture_alt = models.CharField(_('picture alternative text'), max_length=255, blank=True)
    picture_title = models.CharField(_('picture title'), max_length=255, null=True, blank=True)
    picture_author = models.CharField(_('picture author'), max_length=255, blank=True, null=True)
    picture_link = models.URLField(_('picture link'), blank=True, null=True)
    picture_license = models.CharField(_('picture license name'), max_length=255, blank=True, null=True)
    picture_license_link = models.URLField(_('picture license link'), blank=True, null=True)

    sticky = models.BooleanField(_('sticky'), default=False, db_index=True,
                                 help_text=_('Sticky cites will take precedense.'))
    background_plain = models.BooleanField(_('plain background'), default=False)
    background_color = models.CharField(_('background color'), max_length=32, blank=True)
    image = models.ImageField(
        _('background image'), upload_to='social/cite', null=True, blank=True,
        help_text=_('Best background is 975 x 315 px and under 100kB.'))
    image_title = models.CharField(_('background title'), max_length=255, null=True, blank=True)
    image_author = models.CharField(_('background author'), max_length=255, blank=True, null=True)
    image_link = models.URLField(_('background link'), blank=True, null=True)
    image_license = models.CharField(_('background license name'), max_length=255, blank=True, null=True)
    image_license_link = models.URLField(_('background license link'), blank=True, null=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    group = models.ForeignKey(BannerGroup, verbose_name=_('group'), null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('vip', 'text')
        verbose_name = _('banner')
        verbose_name_plural = _('banners')

    def __str__(self):
        t = []
        if self.text:
            t.append(self.text[:60])
        if self.book_id:
            t.append('[ks.]'[:60])
        t.append(self.link[:60])
        if self.vip:
            t.append('vip: ' + self.vip)
        if self.picture:
            t.append('[obr.]')
        if self.video:
            t.append('[vid.]')
        return ', '.join(t)

    def get_absolute_url(self):
        """This is used for testing."""
        return "%s?banner=%d" % (reverse('main_page'), self.id)

    def has_box(self):
        return self.video or self.picture

    def has_body(self):
        return self.vip or self.text or self.book

    def layout(self):
        pieces = []
        if self.has_box():
            pieces.append('box')
        if self.has_body():
            pieces.append('text')
        return '-'.join(pieces)


    def save(self, *args, **kwargs):
        ret = super(Cite, self).save(*args, **kwargs)
        self.clear_cache()
        return ret

    @cached_render('social/cite_promo.html')
    def main_box(self):
        return {
            'cite': self,
            'main': True,
        }

    def clear_cache(self):
        clear_cached_renders(self.main_box)


class Carousel(models.Model):
    placement = models.SlugField(_('placement'), choices=[
        ('main', 'main'),
    ])
    priority = models.SmallIntegerField(_('priority'), default=0)
    language = models.CharField(_('language'), max_length=2, blank=True, default='', choices=settings.LANGUAGES)

    class Meta:
#        ordering = ('placement', '-priority')
        verbose_name = _('carousel')
        verbose_name_plural = _('carousels')

    def __str__(self):
        return self.placement

    @classmethod
    def get(cls, placement):
        carousel = cls.objects.filter(models.Q(language='') | models.Q(language=get_language()), placement=placement).order_by('-priority', '?').first()
        if carousel is None:
            carousel = cls.objects.create(placement=placement)
        return carousel


class CarouselItem(models.Model):
    order = models.PositiveSmallIntegerField(_('order'))
    carousel = models.ForeignKey(Carousel, models.CASCADE, verbose_name=_('carousel'))
    banner = models.ForeignKey(Cite, models.CASCADE, null=True, blank=True, verbose_name=_('banner'))
    banner_group = models.ForeignKey(BannerGroup, models.CASCADE, null=True, blank=True, verbose_name=_('banner group'))

    class Meta:
        ordering = ('order',)
        verbose_name = _('carousel item')
        verbose_name_plural = _('carousel items')

    def __str__(self):
        return str(self.banner or self.banner_group)

    def clean(self):
        if not self.banner and not self.banner_group:
            raise ValidationError(_('Either banner or banner group is required.'))
        elif self.banner and self.banner_group:
            raise ValidationError(_('Either banner or banner group is required.'))

    def get_banner(self):
        return self.banner or self.banner_group.get_banner()
