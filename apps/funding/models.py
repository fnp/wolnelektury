# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import date, datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext as __
import getpaid
from catalogue.models import Book
from polls.models import Poll


class Offer(models.Model):
    """ A fundraiser for a particular book. """
    author = models.CharField(_('author'), max_length=255)
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'))
    description = models.TextField(_('description'), blank=True)
    target = models.DecimalField(_('target'), decimal_places=2, max_digits=10)
    start = models.DateField(_('start'), db_index=True)
    end = models.DateField(_('end'), db_index=True)
    due = models.DateField(_('due'),
        help_text=_('When will it be published if the money is raised.'))
    redakcja_url = models.URLField(_('redakcja URL'), blank=True)
    book = models.ForeignKey(Book, null=True, blank=True,
        help_text=_('Published book.'))
    cover = models.ImageField(_('Cover'), upload_to = 'funding/covers')
    poll = models.ForeignKey(Poll, help_text = _('Poll'),  null = True, on_delete = models.SET_NULL)
        
    def cover_img_tag(self):
        return u'<img src="%s" />' % self.cover.url
    cover_img_tag.short_description = _('Cover preview')
    cover_img_tag.allow_tags = True
        
    class Meta:
        verbose_name = _('offer')
        verbose_name_plural = _('offers')
        ordering = ['-end']

    def __unicode__(self):
        return u"%s - %s" % (self.author, self.title)

    def get_absolute_url(self):
        return reverse('funding_offer', args=[self.slug])

    def is_current(self):
        return self.start <= date.today() <= self.end

    def is_win(self):
        return self.sum() >= self.target

    def remaining(self):
        if self.is_current():
            return None
        if self.is_win():
            return self.sum() - self.target
        else:
            return self.sum()

    @classmethod
    def current(cls):
        """ Returns current fundraiser or None. """
        today = date.today()
        objects = cls.objects.filter(start__lte=today, end__gte=today)
        try:
            return objects[0]
        except IndexError:
            return None

    @classmethod
    def past(cls):
        """ QuerySet for all current and past fundraisers. """
        today = date.today()
        return cls.objects.filter(end__lt=today)

    @classmethod
    def public(cls):
        """ QuerySet for all current and past fundraisers. """
        today = date.today()
        return cls.objects.filter(start__lte=today)

    def get_perks(self, amount=None):
        """ Finds all the perks for the offer.
        
        If amount is provided, returns the perks you get for it.

        """
        perks = Perk.objects.filter(
                models.Q(offer=self) | models.Q(offer=None)
            ).exclude(end_date__lt=date.today())
        if amount is not None:
            perks = perks.filter(price__lte=amount)
        return perks

    def funding_payed(self):
        """ QuerySet for all completed payments for the offer. """
        return Funding.payed().filter(offer=self)

    def sum(self):
        """ The money gathered. """
        return self.funding_payed().aggregate(s=models.Sum('amount'))['s'] or 0


class Perk(models.Model):
    """ A perk offer.
    
    If no attached to a particular Offer, applies to all.

    """
    offer = models.ForeignKey(Offer, verbose_name=_('offer'), null=True, blank=True)
    price = models.DecimalField(_('price'), decimal_places=2, max_digits=10)
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)

    class Meta:
        verbose_name = _('perk')
        verbose_name_plural = _('perks')
        ordering = ['-price']

    def __unicode__(self):
        return "%s (%s%s)" % (self.name, self.price, u" for %s" % self.offer if self.offer else "")


class Funding(models.Model):
    """ A person paying in a fundraiser.

    The payment was completed if and only if payed_at is set.

    """
    offer = models.ForeignKey(Offer, verbose_name=_('offer'))
    name = models.CharField(_('name'), max_length=127, blank=True)
    email = models.EmailField(_('email'), blank=True)
    amount = models.DecimalField(_('amount'), decimal_places=2, max_digits=10)
    payed_at = models.DateTimeField(_('payed at'), null=True, blank=True, db_index=True)
    perks = models.ManyToManyField(Perk, verbose_name=_('perks'), blank=True)

    # Any additional info needed for perks?

    @classmethod
    def payed(cls):
        """ QuerySet for all completed payments. """
        return cls.objects.exclude(payed_at=None)

    class Meta:
        verbose_name = _('funding')
        verbose_name_plural = _('fundings')
        ordering = ['-payed_at']

    def __unicode__(self):
        return unicode(self.offer)

    def get_absolute_url(self):
        return reverse('funding_funding', args=[self.pk])

# Register the Funding model with django-getpaid for payments.
getpaid.register_to_payment(Funding, unique=False, related_name='payment')


class Spent(models.Model):
    """ Some of the remaining money spent on a book. """
    book = models.ForeignKey(Book)
    amount = models.DecimalField(_('amount'), decimal_places=2, max_digits=10)
    timestamp = models.DateField(_('when'))

    class Meta:
        verbose_name = _('money spent on a book')
        verbose_name_plural = _('money spent on books')
        ordering = ['-timestamp']

    def __unicode__(self):
        return u"Spent: %s" % unicode(self.book)


def new_payment_query_listener(sender, order=None, payment=None, **kwargs):
    """ Set payment details for getpaid. """
    payment.amount = order.amount
    payment.currency = 'PLN'
getpaid.signals.new_payment_query.connect(new_payment_query_listener)


def user_data_query_listener(sender, order, user_data, **kwargs):
    """ Set user data for payment. """
    user_data['email'] = order.email
getpaid.signals.user_data_query.connect(user_data_query_listener)

def payment_status_changed_listener(sender, instance, old_status, new_status, **kwargs):
    """ React to status changes from getpaid. """
    if old_status != 'paid' and new_status == 'paid':
        instance.order.payed_at = datetime.now()
        instance.order.save()
getpaid.signals.payment_status_changed.connect(payment_status_changed_listener)
