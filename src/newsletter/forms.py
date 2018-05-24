# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import Form, BooleanField
from django.forms.fields import EmailField
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext

from contact import mailing
from newsletter.models import Subscription
from wolnelektury.utils import send_noreply_mail


class NewsletterForm(Form):
    email_field = 'email'
    agree_newsletter = BooleanField(
        required=False, initial=False, label=_(u'I want to receive Wolne Lektury\'s newsletter.'))

    data_processing_part1 = u'''\
Administratorem danych osobowych jest Fundacja Nowoczesna Polska (ul. Marszałkowska 84/92 lok. 125, 00-514 Warszawa).
Podanie danych osobowych jest dobrowolne.'''
    data_processing_part2 = u'''Dane są przetwarzane w zakresie niezbędnym do wysyłania newslettera odbiorcom.'''
    data_processing_part3 = u'''\
Osobom, których dane są zbierane, przysługuje prawo dostępu do treści swoich danych oraz ich poprawiania.
Więcej informacji w <a href="">polityce prywatności.</a>'''

    @property
    def data_processing(self):
        return mark_safe('%s %s %s' % (self.data_processing_part1, self.data_processing_part2, self.data_processing_part3))

    def save(self, *args, **kwargs):
        try:
            # multiple inheritance mode
            super(NewsletterForm, self).save(*args, **kwargs)
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
            # subscription, created = Subscription.objects.get_or_create(email=email, defaults={'active': False})
            # send_noreply_mail(
            #     ugettext(u'Confirm your subscription to Wolne Lektury newsletter'),
            #     render_to_string('newsletter/subscribe_email.html', {'subscription': subscription}), [email])
            mailing.subscribe(email)


class SubscribeForm(NewsletterForm):
    email = EmailField(label=_('email address'))

    def __init__(self, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)
        self.fields['agree_newsletter'].required = True


class UnsubscribeForm(Form):
    email = EmailField(label=_('email address'))

    def clean(self):
        email = self.cleaned_data.get('email')
        try:
            subscription = Subscription.objects.get(email=email)
        except Subscription.DoesNotExist:
            raise ValidationError(ugettext(u'Email address not found.'))
        self.cleaned_data['subscription'] = subscription

    def save(self):
        subscription = self.cleaned_data['subscription']
        subscription.active = False
        subscription.save()

        context = {'subscription': subscription}
        # refactor to send_noreply_mail
        send_noreply_mail(
            ugettext(u'Unsubscribe from Wolne Lektury\'s newsletter.'),
            render_to_string('newsletter/unsubscribe_email.html', context),
            [subscription.email], fail_silently=True)
