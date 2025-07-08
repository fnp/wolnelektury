# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from oauthlib.common import urlencode, generate_token
from random import randint
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from catalogue.models import Book
from wolnelektury.utils import cached_render, clear_cached_renders


class BannerGroup(models.Model):
    name = models.CharField('nazwa', max_length=255, unique=True)
    created_at = models.DateTimeField('utworzona', auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'grupa bannerów'
        verbose_name_plural = 'grupy bannerów'

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
    book = models.ForeignKey(Book, models.CASCADE, verbose_name='książka', null=True, blank=True)
    text = models.TextField('tekst', blank=True)
    small = models.BooleanField(
        'mały', default=False, help_text='Sprawia, że cytat wyświetla się mniejszym fontem.')
    vip = models.CharField('VIP', max_length=128, null=True, blank=True)
    link = models.URLField('odnośnik')
    video = models.URLField('wideo', blank=True)
    picture = models.ImageField('ilustracja', blank=True,
            help_text='Najlepsze wymiary: 975 x 315 z tekstem, 487 x 315 bez tekstu.')
    picture_alt = models.CharField('alternatywny tekst ilustracji', max_length=255, blank=True)
    picture_title = models.CharField('tytuł ilustracji', max_length=255, null=True, blank=True)
    picture_author = models.CharField('autor ilustracji', max_length=255, blank=True, null=True)
    picture_link = models.URLField('link ilustracji', blank=True, null=True)
    picture_license = models.CharField('nazwa licencji ilustracji', max_length=255, blank=True, null=True)
    picture_license_link = models.URLField('adres licencji ilustracji', blank=True, null=True)

    sticky = models.BooleanField('przyklejony', default=False, db_index=True,
                                 help_text='Przyklejone cytaty mają pierwszeństwo.')
    background_plain = models.BooleanField('jednobarwne tło', default=False)
    background_color = models.CharField('kolor tła', max_length=32, blank=True)
    image = models.ImageField(
        'obraz tła', upload_to='social/cite', null=True, blank=True,
        help_text='Najlepsze tło ma wielkość 975 x 315 px i waży poniżej 100kB.')
    image_title = models.CharField('tytuł obrazu tła', max_length=255, null=True, blank=True)
    image_author = models.CharField('autor obrazu tła', max_length=255, blank=True, null=True)
    image_link = models.URLField('link obrazu tła', blank=True, null=True)
    image_license = models.CharField('nazwa licencji obrazu tła', max_length=255, blank=True, null=True)
    image_license_link = models.URLField('adres licencji obrazu tła', blank=True, null=True)

    created_at = models.DateTimeField('utworzony', auto_now_add=True)
    group = models.ForeignKey(BannerGroup, verbose_name='grupa', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('vip', 'text')
        verbose_name = 'banner'
        verbose_name_plural = 'bannery'

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
    placement = models.SlugField('miejsce', choices=[
        ('main', 'main'),
        ('main_2022', 'main 2022'),
    ])
    priority = models.SmallIntegerField('priorytet', default=0)
    language = models.CharField('język', max_length=2, blank=True, default='', choices=settings.LANGUAGES)

    class Meta:
#        ordering = ('placement', '-priority')
        verbose_name = 'karuzela'
        verbose_name_plural = 'karuzele'

    def __str__(self):
        return self.placement

    @classmethod
    def get(cls, placement):
        carousel = cls.objects.filter(placement=placement).order_by('-priority', '?').first()
        if carousel is None:
            carousel = cls.objects.create(placement=placement)
        return carousel


class CarouselItem(models.Model):
    order = models.PositiveSmallIntegerField('kolejność')
    carousel = models.ForeignKey(Carousel, models.CASCADE, verbose_name='karuzela')
    banner = models.ForeignKey(
        Cite, models.CASCADE, null=True, blank=True, verbose_name='banner')
    banner_group = models.ForeignKey(
        BannerGroup, models.CASCADE, null=True, blank=True, verbose_name='grupa bannerów')

    class Meta:
        ordering = ('order',)
        verbose_name = 'element karuzeli'
        verbose_name_plural = 'elementy karuzeli'

    def __str__(self):
        return str(self.banner or self.banner_group)

    def clean(self):
        if not self.banner and not self.banner_group:
            raise ValidationError('Proszę wskazać banner albo grupę bannerów.')
        elif self.banner and self.banner_group:
            raise ValidationError('Proszę wskazać banner albo grupę bannerów.')

    def get_banner(self):
        return self.banner or self.banner_group.get_banner()


class UserConfirmation(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=128, unique=True)

    def send(self):
        send_mail(
            'Potwierdź konto w bibliotece Wolne Lektury',
            f'https://beta.wolnelektury.pl/ludzie/potwierdz/{self.key}/',
            settings.CONTACT_EMAIL,
            [self.user.email]
        )

    def use(self):
        user = self.user
        user.is_active = True
        user.save()
        self.delete()
    
    @classmethod
    def request(cls, user):
        cls.objects.create(
            user=user,
            key=generate_token()
        ).send()



class Progress(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    book = models.ForeignKey('catalogue.Book', models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_mode = models.CharField(max_length=64, choices=[
        ('text', 'text'),
        ('audio', 'audio'),
    ])
    text_percent = models.FloatField(null=True, blank=True)
    text_anchor = models.CharField(max_length=64, blank=True)
    audio_percent = models.FloatField(null=True, blank=True)
    audio_timestamp = models.FloatField(null=True, blank=True)
    implicit_text_percent = models.FloatField(null=True, blank=True)
    implicit_text_anchor = models.CharField(max_length=64, blank=True)
    implicit_audio_percent = models.FloatField(null=True, blank=True)
    implicit_audio_timestamp = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = [('user', 'book')]

    def save(self, *args, **kwargs):
        audio_l = self.book.get_audio_length()
        if self.text_anchor:
            self.text_percent = 33
            if audio_l:
                self.implicit_audio_percent = 40
                self.implicit_audio_timestamp = audio_l * .4
        if self.audio_timestamp:
            if self.audio_timestamp > audio_l:
                self.audio_timestamp = audio_l
            if audio_l:
                self.audio_percent = 100 * self.audio_timestamp / audio_l
                self.implicit_text_percent = 60
                self.implicit_text_anchor = 'f20'
        return super().save(*args, **kwargs)
