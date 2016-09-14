# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import Form, BooleanField
from django.forms.fields import EmailField
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, ugettext

from newsletter.models import Subscription
from wolnelektury.utils import send_noreply_mail


class NewsletterForm(Form):
    email_field = 'email'
    agree_newsletter = BooleanField(
        required=False, initial=True, label=_(u'I want to receive Wolne Lektury\'s newsletter.'), help_text='''\
Oświadczam, że wyrażam zgodę na przetwarzanie moich danych osobowych zawartych \
w niniejszym formularzu zgłoszeniowym przez Fundację Nowoczesna Polska (administratora danych) z siedzibą \
w Warszawie (00-514) przy ul. Marszałkowskiej 84/92 lok. 125 w celu otrzymywania newslettera Wolnych Lektur. \
Jednocześnie oświadczam, że zostałam/em poinformowana/y o tym, że mam prawo wglądu w treść swoich danych i \
możliwość ich poprawiania oraz że ich podanie jest dobrowolne, ale niezbędne do dokonania zgłoszenia.''')

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
            subscription, created = Subscription.objects.get_or_create(email=email, defaults={'active': False})
            send_noreply_mail(
                ugettext(u'Confirm your subscription to Wolne Lektury newsletter'),
                render_to_string('newsletter/subscribe_email.html', {'subscription': subscription}), [email])


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
