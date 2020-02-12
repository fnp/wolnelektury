from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template import Template, Context
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from sentry_sdk import capture_exception
from catalogue.utils import get_random_hash
from .states import Level, states


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
        state = self.get_state(time=time)
        contacts = state.get_contacts()
    
        contacts = contacts.exclude(emailsent__template=self)
        for contact in contacts:
            if not contact.is_annoyed:
                self.send(contact, verbose=verbose, dry_run=dry_run)

    def get_state(self, time=None, test=False):
        for s in states:
            if s.slug == self.state:
                return s(
                    time=time,
                    min_days_since=self.min_days_since,
                    max_days_since=self.max_days_since,
                    test=test
                )
        raise ValueError('Unknown state', s.state)

    def send(self, contact, verbose=False, dry_run=False, test=False):
        state = self.get_state(test=test)
        ctx = state.get_context(contact)
        ctx['contact'] = contact
        ctx = Context(ctx)

        subject = Template(self.subject).render(ctx)
        if test:
            subject = "[test] " + subject

        body_template = '{% extends "messaging/email_body.html" %}{% block body %}' + self.body + '{% endblock %}'
        body = Template(body_template).render(ctx)

        if verbose:
            print(contact.email, subject)
        if not dry_run:
            try:
                send_mail(subject, body, settings.CONTACT_EMAIL, [contact.email], fail_silently=False)
            except:
                capture_exception()
            else:
                if not test:
                    self.emailsent_set.create(
                        contact=contact,
                        subject=subject,
                        body=body,
                    )

    def send_test_email(self, email):
        contact = Contact(
                email=email,
                key='test'
            )
        self.send(contact, test=True)


class Contact(models.Model):
    email = models.EmailField(unique=True)
    level = models.PositiveSmallIntegerField(
        choices=[
            (Level.COLD, _('Cold')),
            (Level.TRIED, _('Would-be donor')),
            (Level.SINGLE, _('One-time donor')),
            (Level.RECURRING, _('Recurring donor')),
            (Level.OPT_OUT, _('Opt out')),
        ])
    since = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    key = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = get_random_hash(self.email)
        super().save(*args, **kwargs)

    @property
    def is_annoyed(self):
        cutoff = now() - timedelta(settings.MESSAGING_MIN_DAYS)
        return self.emailsent_set.filter(timestamp__gte=cutoff).exists()

    def get_optout_url(self):
        return reverse('messaging_optout', args=[self.key])

    @classmethod
    def update(cls, email, level, since, expires_at=None):
        obj, created = cls.objects.get_or_create(email=email, defaults={
                "level": level,
                "since": since,
                "expires_at": expires_at
            })
        if not created:
            obj.ascend(level, since, expires_at)

    def ascend(self, level, since=None, expires_at=None):
        if since is None:
            since = now()
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


class EmailSent(models.Model):
    template = models.ForeignKey(EmailTemplate, models.CASCADE)
    contact = models.ForeignKey(Contact, models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(_('subject'), max_length=1024)
    body = models.TextField(_('body'))

    class Meta:
        verbose_name = _('email sent')
        verbose_name_plural = _('emails sent')
        ordering = ('-timestamp',)

    def __str__(self):
        return '%s %s' % (self.email, self.timestamp)

