from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _
from sentry_sdk import capture_exception
from .recipient import Recipient
from .states import states


class EmailTemplate(models.Model):
    state = models.CharField(_('state'), max_length=128, choices=[(s.slug, s.name) for s in states], help_text='?')
    subject = models.CharField(_('subject'), max_length=1024)
    body = models.TextField(_('body'))
    min_days_since = models.SmallIntegerField(_('min days since'), null=True, blank=True)
    max_days_since = models.SmallIntegerField(_('max days since'), null=True, blank=True)
    min_hour = models.PositiveSmallIntegerField(_('min hour'), null=True, blank=True)
    max_hour = models.PositiveSmallIntegerField(_('max hour'), null=True, blank=True)
    min_day_of_month = models.PositiveSmallIntegerField(_('min day of month'), null=True, blank=True)
    max_day_of_month = models.PositiveSmallIntegerField(_('max day of month'), null=True, blank=True)
    dow_1 = models.BooleanField(_('Monday'), default=True)
    dow_2 = models.BooleanField(_('Tuesday'), default=True)
    dow_3 = models.BooleanField(_('Wednesday'), default=True)
    dow_4 = models.BooleanField(_('Thursday'), default=True)
    dow_5 = models.BooleanField(_('Friday'), default=True)
    dow_6 = models.BooleanField(_('Saturday'), default=True)
    dow_7 = models.BooleanField(_('Sunday'), default=True)
    is_active = models.BooleanField(_('active'), default=False)

    class Meta:
        verbose_name = _('email template')
        verbose_name_plural = _('email templates')

    def __str__(self):
        return '%s (%+d)' % (self.get_state_display(), self.min_days_since or 0)

    def run(self, time=None, verbose=False, dry_run=False):
        state = self.get_state()
        recipients = state(time=time, offset=self.days).get_recipients()
        hash_values = set(recipient.hash_value for recipient in recipients)
        sent = set(EmailSent.objects.filter(
                template=self, hash_value__in=hash_values
            ).values_list('hash_value', flat=True))
        for recipient in recipients:
            if recipient.hash_value in sent:
                continue
            self.send(recipient, verbose=verbose, dry_run=dry_run)

    def get_state(self):
        for s in states:
            if s.slug == self.state:
                return s
        raise ValueError('Unknown state', s.state)

    def send(self, recipient, verbose=False, dry_run=False, test=False):
        subject = Template(self.subject).render(Context(recipient.context))
        body = Template(self.body).render(Context(recipient.context))
        if verbose:
            print(recipient.email, subject)
        if not dry_run:
            try:
                send_mail(subject, body, settings.CONTACT_EMAIL, [recipient.email], fail_silently=False)
            except:
                capture_exception()
            else:
                if not test:
                    self.emailsent_set.create(
                        hash_value=recipient.hash_value,
                        email=recipient.email,
                        subject=subject,
                        body=body,
                    )

    def send_test_email(self, email):
        state = self.get_state()()
        recipient = state.get_example_recipient(email)
        self.send(recipient, test=True)


class EmailSent(models.Model):
    template = models.ForeignKey(EmailTemplate, models.CASCADE)
    hash_value = models.CharField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)
    email = models.CharField(_('e-mail'), max_length=1024)
    subject = models.CharField(_('subject'), max_length=1024)
    body = models.TextField(_('body'))

    class Meta:
        verbose_name = _('email sent')
        verbose_name_plural = _('emails sent')
        ordering = ('-timestamp',)

    def __str__(self):
        return '%s %s' % (self.email, self.timestamp)


class Contact(models.Model):
    COLD = 10
    TRIED = 20
    SINGLE = 30
    RECURRING = 40
    OPT_OUT = 50

    email = models.EmailField(unique=True)
    level = models.PositiveSmallIntegerField(
        choices=[
            (TRIED, _('Would-be donor')),
            (SINGLE, _('One-time donor')),
            (RECURRING, _('Recurring donor')),
            (COLD, _('Cold')),
            (OPT_OUT, _('Opt out')),
        ])
    since = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def update(cls, email, level, since, expires_at=None):
        obj, created = cls.objects.get_or_create(email=email, defaults={
                "level": level,
                "since": since,
                "expires_at": expires_at
            })
        if not created:
            obj.ascend(level, since, expires_at)

    def ascend(self, level, since, expires_at=None):
        if level < self.level:
            return
        if level == self.level:
            self.since = min(since, self.since)

            if expires_at and self.expires_at:
                self.expires_at = max(expires_at, self.expires_at)
            else:
                self.expires_at = expires_at
        else:
            self.level = level
            self.since = since
            self.expires_at = expires_at
        self.save()

