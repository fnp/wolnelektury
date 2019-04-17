from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _, ungettext, ugettext, get_language
from catalogue.utils import get_random_hash
from .payment_methods import methods, method_by_slug
from .payu import models as payu_models


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
    active = models.BooleanField(_('active'), default=True)

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
            return datetime.max - timedelta(1)
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
    is_cancelled = models.BooleanField(_('cancelled'), default=False)
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expires_at'), null=True, blank=True)

    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')

    def __str__(self):
        return self.key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = get_random_hash(self.email)
        return super(Schedule, self).save(*args, **kwargs)

    def initiate_payment(self, request):
        return self.get_payment_method().initiate(request, self)

    def pay(self, request):
        return self.get_payment_method().pay(request, self)

    def get_absolute_url(self):
        return reverse('club_schedule', args=[self.key])

    def get_payment_method(self):
        return method_by_slug[self.method]

    def is_expired(self):
        return self.expires_at is not None and self.expires_at <= now()

    def is_active(self):
        return self.expires_at is not None and self.expires_at > now()


class Membership(models.Model):
    """ Represents a user being recognized as a member of the club. """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    name = models.CharField(max_length=255, blank=True)
    honorary = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')

    def __str__(self):
        return u'tow. ' + str(self.user)

    @classmethod
    def is_active_for(cls, user):
        if user.is_anonymous:
            return False
        try:
            membership = user.membership
        except cls.DoesNotExist:
            return False
        if membership.honorary:
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
            self.schedule.get_absolute_url())

    def get_description(self):
        return ugettext('Towarzystwo Wolnych Lektur')

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
            since = self.schedule.expires_at or now()
            new_exp = self.schedule.plan.get_next_installment(since)
            if self.schedule.expires_at is None or self.schedule.expires_at < new_exp:
                self.schedule.expires_at = new_exp
                self.schedule.save()


class PayUCardToken(payu_models.CardToken):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)


class PayUNotification(payu_models.Notification):
    order = models.ForeignKey(PayUOrder, models.CASCADE, related_name='notification_set')
