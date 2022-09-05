# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import datetime, timedelta
import os
import tempfile
from django.apps import apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail, EmailMessage
from django.urls import reverse
from django.db import models
from django import template
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _, ungettext, ugettext, get_language
from django_countries.fields import CountryField
from catalogue.utils import get_random_hash
from messaging.states import Level
from reporting.utils import render_to_pdf
from .payment_methods import methods
from .payu import models as payu_models
from .civicrm import report_activity
from . import utils


class Club(models.Model):
    min_amount = models.IntegerField(_('minimum amount'))
    min_for_year = models.IntegerField(_('minimum amount for year'))
    default_single_amount = models.IntegerField(_('default single amount'))
    default_monthly_amount = models.IntegerField(_('default monthly amount'))

    class Meta:
        verbose_name = _('club')
        verbose_name_plural = _('clubs')
    
    def __str__(self):
        return 'Klub'


class SingleAmount(models.Model):
    club = models.ForeignKey(Club, models.CASCADE)
    amount = models.IntegerField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['amount']

class MonthlyAmount(models.Model):
    club = models.ForeignKey(Club, models.CASCADE)
    amount = models.IntegerField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['amount']


class Consent(models.Model):
    order = models.IntegerField()
    active = models.BooleanField(default=True)
    text = models.CharField(max_length=2048)
    required = models.BooleanField()

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.text


class Schedule(models.Model):
    """ Represents someone taking up a plan. """
    key = models.CharField(_('key'), max_length=255, unique=True)
    email = models.EmailField(_('email'))
    membership = models.ForeignKey('Membership', verbose_name=_('membership'), null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    method = models.CharField(_('method'), max_length=32, choices=[
        (m.slug, m.name) for m in methods
        ])
    monthly = models.BooleanField(_('monthly'), default=True)
    yearly = models.BooleanField(_('yearly'), default=False)

    source = models.CharField(_('source'), max_length=255, blank=True)

    is_cancelled = models.BooleanField(_('cancelled'), default=False)
    payed_at = models.DateTimeField(_('payed at'), null=True, blank=True)
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expires_at'), null=True, blank=True)
    email_sent = models.BooleanField(default=False)

    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    postal = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)
    postal_town = models.CharField(max_length=255, blank=True)
    postal_country = CountryField(default='PL', blank=True)

    consent = models.ManyToManyField(Consent)
    
    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')

    def __str__(self):
        return self.key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = get_random_hash(self.email)
        super(Schedule, self).save(*args, **kwargs)
        self.update_contact()

    def initiate_payment(self, request):
        return self.get_payment_method().initiate(request, self)

    def pay(self, request):
        return self.get_payment_method().pay(request, self)

    def get_absolute_url(self):
        return reverse('club_schedule', args=[self.key])

    def get_thanks_url(self):
        return reverse('club_thanks', args=[self.key])

    def get_payment_method(self):
        return [m for m in methods if m.slug == self.method][0]

    def get_payment_methods(self):
        for method in methods:
            if (self.monthly or self.yearly) and method.is_recurring:
                yield method
            elif not (self.monthly or self.yearly) and method.is_onetime:
                yield method

    def is_expired(self):
        return self.expires_at is not None and self.expires_at <= now()

    def is_active(self):
        return self.payed_at is not None and (self.expires_at is None or self.expires_at > now())

    def is_recurring(self):
        return self.monthly or self.yearly

    def set_payed(self):
        since = self.expires_at
        n = now()
        if since is None or since < n:
            since = n
        new_exp = self.get_next_installment(since)
        if self.payed_at is None:
            self.payed_at = n
        if self.expires_at is None or self.expires_at < new_exp:
            self.expires_at = new_exp
            self.save()

        if not self.email_sent:
            self.send_email()
    
    def get_next_installment(self, date):
        if self.yearly:
            return utils.add_year(date)
        if self.monthly:
            return utils.add_month(date)
        club = Club.objects.first()
        if club is not None and self.amount >= club.min_for_year:
            return utils.add_year(date)
        return utils.add_month(date)

    def get_other_active_recurring(self):
        schedules = type(self).objects.exclude(
            monthly=False, yearly=False
        ).filter(is_cancelled=False, expires_at__gt=now()).exclude(pk=self.pk)
        mine_q = models.Q(email=self.email)
        if self.membership is not None:
            mine_q |= models.Q(membership__user=self.membership.user)
        schedules = schedules.filter(mine_q)
        return schedules.order_by('-expires_at').first()
    
    def send_email(self):
        ctx = {'schedule': self}
        send_mail(
            template.loader.render_to_string('club/email/thanks_subject.txt', ctx).strip(),
            template.loader.render_to_string('club/email/thanks.txt', ctx),
            settings.CONTACT_EMAIL, [self.email], fail_silently=False)
        self.email_sent = True
        self.save()

    def send_email_failed_recurring(self):
        ctx = {
            'schedule': self,
            'other': self.get_other_active_recurring(),
        }
        send_mail(
            'Darowizna na Wolne Lektury — problem z płatnością',
            template.loader.render_to_string('club/email/failed_recurring.txt', ctx),
            settings.CONTACT_EMAIL, [self.email], fail_silently=False
        )
        
    def update_contact(self):
        Contact = apps.get_model('messaging', 'Contact')
        if not self.payed_at:
            level = Level.TRIED
            since = self.started_at
        else:
            since = self.payed_at
            if self.is_recurring():
                level = Level.RECURRING
            else:
                level = Level.SINGLE
        Contact.update(self.email, level, since, self.expires_at)





class Membership(models.Model):
    """ Represents a user being recognized as a member of the club. """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    name = models.CharField(_('name'), max_length=255, blank=True)
    manual = models.BooleanField(_('manual'), default=False)
    notes = models.CharField(_('notes'), max_length=2048, blank=True)
    updated_at = models.DateField(_('updated at'), auto_now=True, blank=True)

    class Meta:
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_contact()

    def update_contact(self):
        email = self.user.email
        if not email:
            return

        Contact = apps.get_model('messaging', 'Contact')
        if self.manual:
            Contact.update(email, Level.MANUAL_MEMBER, self.updated_at)
        else:
            Contact.reset(email)

    @classmethod
    def is_active_for(cls, user):
        if user.is_anonymous:
            return False
        try:
            membership = user.membership
        except cls.DoesNotExist:
            return False
        if membership.manual:
            return True
        return Schedule.objects.filter(
                expires_at__gt=now(),
                membership__user=user,
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


class Ambassador(models.Model):
    name = models.CharField(_('name'), max_length=255)
    photo = models.ImageField(_('photo'), blank=True)
    text = models.CharField(_('text'), max_length=1024)

    class Meta:
        verbose_name = _('ambassador')
        verbose_name_plural = _('ambassadors')
        ordering = ['name']
    
    def __str__(self):
        return self.name

        
########
#      #
# PayU #
#      #
########

class PayUOrder(payu_models.Order):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)

    def get_amount(self):
        return self.schedule.amount

    def get_buyer(self):
        return {
            "email": self.schedule.email,
            "language": get_language(),
        }

    def get_continue_url(self):
        return "https://{}{}".format(
            Site.objects.get_current().domain,
            self.schedule.get_thanks_url())

    def get_description(self):
        return 'Wolne Lektury'

    def is_recurring(self):
        return self.schedule.get_payment_method().is_recurring

    def get_card_token(self):
        return self.schedule.payucardtoken_set.order_by('-created_at').first()

    def get_notify_url(self):
        return "https://{}{}".format(
            Site.objects.get_current().domain,
            reverse('club_payu_notify', args=[self.pk]))

    def status_updated(self):
        if self.status == 'COMPLETED':
            self.schedule.set_payed()

        elif self.status == 'CANCELED' or self.status.startswith('ERR-'):
            if self.is_recurring() and self.schedule.expires_at:
                self.schedule.send_email_failed_recurring()
            
        self.report_activity()

    @property
    def updated_at(self):
        try:
            return self.notification_set.all().order_by('-received_at')[0].received_at
        except IndexError:
            return None
    
    def report_activity(self):
        if self.status not in ['COMPLETED', 'CANCELED', 'REJECTED']:
            return

        if self.status != 'COMPLETED':
            name = settings.CIVICRM_ACTIVITIES['Failed contribution']
        elif self.is_recurring():
            name = settings.CIVICRM_ACTIVITIES['Recurring contribution']
        else:
            name = settings.CIVICRM_ACTIVITIES['Contribution']

        report_activity.delay(
            self.schedule.email,
            self.schedule.key,
            f'payu:{self.id}',
            name,
            self.updated_at,
            {
                'kwota': self.schedule.amount,
            }
        )            

    @classmethod
    def send_receipt(cls, email, year, resend=False):
        Contact = apps.get_model('messaging', 'Contact')
        Funding = apps.get_model('funding', 'Funding')
        BillingAgreement = apps.get_model('paypal', 'BillingAgreement')
        payments = []

        try:
            contact = Contact.objects.get(email=email)
        except Contact.DoesNotExist:
            funding = Funding.objects.filter(
                email=email,
                payed_at__year=year,
                notifications=True).order_by('payed_at').first()
            if funding is None:
                print('no notifications')
                return
            optout = funding.wl_optout_url()
        else:
            if contact.level == Level.OPT_OUT:
                print('opt-out')
                return
            optout = contact.wl_optout_url()

        qs = cls.objects.filter(status='COMPLETED', schedule__email=email, completed_at__year=year).order_by('completed_at')
        for order in qs:
            payments.append({
                'timestamp': order.completed_at,
                'amount': order.get_amount(),
            })

        for ba in BillingAgreement.objects.filter(schedule__email=email):
            payments.extend(ba.get_donations(year))

        fundings = Funding.objects.filter(
            email=email,
            payed_at__year=year
        ).order_by('payed_at')
        for funding in fundings:
            payments.append({
                'timestamp': funding.payed_at,
                'amount': funding.amount,
            })

        if not payments: return

        payments.sort(key=lambda x: x['timestamp'])

        ctx = {
            "email": email,
            "year": year,
            "next_year": year + 1,
            "total": sum(x['amount'] for x in payments),
            "payments": payments,
            "optout": optout,
            "resend": resend,
        }
        temp = tempfile.NamedTemporaryFile(prefix='receipt-', suffix='.pdf', delete=False)
        temp.close()
        render_to_pdf(temp.name, 'club/receipt.texml', ctx, {
            "fnp.eps": os.path.join(settings.STATIC_ROOT, "img/fnp.eps"),
            })

        message = EmailMessage(
                'Odlicz darowiznę na Wolne Lektury od podatku',
                template.loader.render_to_string('club/receipt_email.txt', ctx),
                settings.CONTACT_EMAIL, [email]
            )
        with open(temp.name, 'rb') as f:
            message.attach('wolnelektury-darowizny.pdf', f.read(), 'application/pdf')
        message.send()
        os.unlink(f.name)


class PayUCardToken(payu_models.CardToken):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)


class PayUNotification(payu_models.Notification):
    order = models.ForeignKey(PayUOrder, models.CASCADE, related_name='notification_set')
