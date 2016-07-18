# -*- coding: utf-8 -*-

from django.forms import Form, BooleanField
from django.utils.translation import ugettext_lazy as _

from newsletter.models import Subscription


class NewsletterForm(Form):
    email_field = 'email'
    agree_newsletter = BooleanField(required=False, label=_(u'I want to receive Wolne Lektury\'s newsletter.'))

    def save(self):
        try:
            # multiple inheritance mode
            super(NewsletterForm, self).save()
        except AttributeError:
            pass
        email = self.cleaned_data[self.email_field]
        subscription, created = Subscription.objects.get_or_create(email=email)
        if not created and not subscription.active:
            subscription.active = True
            subscription.save()
        # Send some test email?
