# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext as __
from datetime import date, datetime
from catalogue.models import Book


class Offer(models.Model):
    author = models.CharField(_('author'), max_length=255)
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'))
    book = models.ForeignKey(Book, null=True, blank=True)
    redakcja_url = models.URLField(_('redakcja URL'), blank=True)
    target = models.DecimalField(_('target'), decimal_places=2, max_digits=10)
    start = models.DateField(_('start'))
    end = models.DateField(_('end'))

    class Meta:
        verbose_name = _('offer')
        verbose_name_plural = _('offers')
        ordering = ['-end']

    def __unicode__(self):
        return u"%s – %s" % (self.author, self.title)

    def get_absolute_url(self):
        return reverse('funding_offer', args=[self.slug])

    @classmethod
    def current(cls):
        today = date.today()
        objects = cls.objects.filter(start__lte=today, end__gte=today)
        try:
            return objects[0]
        except IndexError:
            return None

    @classmethod
    def public(cls):
        today = date.today()
        return cls.objects.filter(start__lte=today)        

    def get_perks(self, amount=None):
        perks = Perk.objects.filter(
                models.Q(offer=self) | models.Q(offer=None)
            )
        if amount is not None:
            perks = perks.filter(price__lte=amount)
        return perks

    def fund(self, name, email, amount):
        funding = self.funding_set.create(
            name=name, email=email, amount=amount,
            payed_at=datetime.now())
        funding.perks = self.get_perks(amount)
        return funding

    def sum(self):
        return self.funding_set.aggregate(s=models.Sum('amount'))['s'] or 0

    def state(self):
        if self.sum() >= self.target:
            return 'win'
        elif self.start <= date.today() <= self.end:
            return 'running'
        else:
            return 'lose'


class Perk(models.Model):
    offer = models.ForeignKey(Offer, verbose_name=_('offer'), null=True, blank=True)
    price = models.DecimalField(_('price'), decimal_places=2, max_digits=10)
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        verbose_name = _('perk')
        verbose_name_plural = _('perks')
        ordering = ['-price']

    def __unicode__(self):
        return "%s (%s%s)" % (self.name, self.price, u" for %s" % self.offer if self.offer else "")


class Funding(models.Model):
    offer = models.ForeignKey(Offer, verbose_name=_('offer'))
    name = models.CharField(_('name'), max_length=127)
    email = models.EmailField(_('email'))
    amount = models.DecimalField(_('amount'), decimal_places=2, max_digits=10)
    payed_at = models.DateTimeField(_('payed_at'))
    perks = models.ManyToManyField(Perk, verbose_name=_('perks'), blank=True)

    class Meta:
        verbose_name = _('funding')
        verbose_name_plural = _('fundings')
        ordering = ['-payed_at']

    def __unicode__(self):
        return "%s payed %s for %s" % (self.name, self.amount, self.offer)


class Spent(models.Model):
    amount = models.DecimalField(_('amount'), decimal_places=2, max_digits=10)
    timestamp = models.DateField(_('when'))
    book = models.ForeignKey(Book)

    def __unicode__(self):
        return u"Spent: %s" % unicode(self.book)
