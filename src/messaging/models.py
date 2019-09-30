from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _
from sentry_sdk import capture_exception
from .states import states


class EmailTemplate(models.Model):
    state = models.CharField(_('state'), max_length=128, choices=[(s.slug, s.name) for s in states], help_text='?')
    subject = models.CharField(_('subject'), max_length=1024)
    body = models.TextField(_('body'))
    days = models.SmallIntegerField(_('days'), null=True, blank=True)
    hour = models.IntegerField(_('hour'), null=True, blank=True)

    class Meta:
        verbose_name = _('email template')
        verbose_name_plural = _('email templates')

    def __str__(self):
        return '%s (%+d)' % (self.get_state_display(), self.days)
        return self.subject

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

    def send(self, recipient, verbose=False, dry_run=False):
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
                self.emailsent_set.create(
                    hash_value=recipient.hash_value,
                    email=recipient.email,
                    subject=subject,
                    body=body,
                )



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
