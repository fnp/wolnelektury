# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import timedelta
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _, ungettext
from catalogue.utils import get_random_hash
from .payment_methods import methods, method_by_slug


class Plan(models.Model):
    """ Plans are set up by administrators. """
    MONTH = 30
    YEAR = 365
    PERPETUAL = 999
    intervals = [
        (MONTH, _('a month')),
        (YEAR, _('a year')),
        (PERPETUAL, _('in perpetuity')),
    ]

    interval = models.SmallIntegerField(_('inteval'), choices=intervals)
    min_amount = models.DecimalField(_('min_amount'), max_digits=10, decimal_places=2)
    allow_recurring = models.BooleanField(_('allow recurring'))
    allow_one_time = models.BooleanField(_('allow one time'))

    class Meta:
        verbose_name = _('plan')
        verbose_name_plural = _('plans')

    def __str__(self):
        return "%s %s" % (self.min_amount, self.get_interval_display())
    
    class Meta:
        ordering = ('interval',)

    def payment_methods(self):
        for method in methods:
            if self.allow_recurring and method.is_recurring or self.allow_one_time and not method.is_recurring:
                yield method

    def get_next_installment(self, date):
        if self.interval == self.PERPETUAL:
            return None
        elif self.interval == self.YEAR:
            return date.replace(year=date.year + 1)
        elif self.interval == self.MONTH:
            day = date.day
            date = (date.replace(day=1) + timedelta(31)).replace(day=1) + timedelta(day - 1)
            if date.day != day:
                date = date.replace(day=1)
            return date
            


class Schedule(models.Model):
    """ Represents someone taking up a plan. """
    key = models.CharField(_('key'), max_length=255, unique=True)
    email = models.EmailField(_('email'))
    membership = models.ForeignKey('Membership', verbose_name=_('membership'), null=True, blank=True, on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, verbose_name=_('plan'), on_delete=models.PROTECT)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    method = models.CharField(_('method'), max_length=255, choices=[(method.slug, method.name) for method in methods])
    is_active = models.BooleanField(_('active'), default=False)
    is_cancelled = models.BooleanField(_('cancelled'), default=False)
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expires_at'), null=True, blank=True)
    # extra info?

    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')

    def __str__(self):
        return self.key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = get_random_hash(self.email)
        return super(Schedule, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('club_schedule', args=[self.key])

    def get_payment_method(self):
        return method_by_slug[self.method]

    def is_expired(self):
        return self.expires_at is not None and self.expires_at < now()

    def create_payment(self):
        n = now()
        self.expires_at = self.plan.get_next_installment(n)
        self.is_active = True
        self.save()
        self.payment_set.create(payed_at=n)


class Payment(models.Model):
    schedule = models.ForeignKey(Schedule, verbose_name=_('schedule'), on_delete=models.PROTECT)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    payed_at = models.DateTimeField(_('payed at'), null=True, blank=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __str__(self):
        return "%s %s" % (self.schedule, self.payed_at)


class Membership(models.Model):
    """ Represents a user being recognized as a member of the club. """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')

    def __str__(self):
        return u'tow. ' + str(self.user)

    @classmethod
    def is_active_for(self, user):
        if user.is_anonymous:
            return False
        return Schedule.objects.filter(
                models.Q(expires_at=None) | models.Q(expires_at__lt=now()),
                membership__user=user,
                is_active=True,
            ).exists()


class ReminderEmail(models.Model):
    days_before = models.SmallIntegerField(_('days before'))
    subject = models.CharField(_('subject'), max_length=1024)
    body = models.TextField(_('body'))

    class Meta:
        verbose_name = _('reminder email')
        verbose_name_plural = _('reminder emails')
        ordering = ['days_before']

    def __str__(self):
        if self.days_before >= 0:
            return ungettext('a day before expiration', '%d days before expiration', n=self.days_before)
        else:
            return ungettext('a day after expiration', '%d days after expiration', n=-self.days_before)

