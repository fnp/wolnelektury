# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import Form, BooleanField
from django.utils.translation import ugettext_lazy as _

from newsletter.models import Subscription


class NewsletterForm(Form):
    email_field = 'email'
    agree_newsletter = BooleanField(
        required=False, initial=True, label=_(u'I want to receive Wolne Lektury\'s newsletter.'))

    def save(self):
        try:
            # multiple inheritance mode
            super(NewsletterForm, self).save()
        except AttributeError:
            pass
        if not self.cleaned_data.get('agree_newsletter'):
            return
        email = self.cleaned_data[self.email_field]
        try:
            validate_email(email)
        except ValidationError:
            pass
        else:
            subscription, created = Subscription.objects.get_or_create(email=email)
            if not created and not subscription.active:
                subscription.active = True
                subscription.save()
            # Send some test email?
