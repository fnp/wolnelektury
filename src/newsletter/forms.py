# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import Form, BooleanField
from django.forms.fields import EmailField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from newsletter.subscribe import subscribe
from .models import Newsletter


class NewsletterForm(Form):
    email_field = 'email'
    agree_newsletter = BooleanField(
        required=False, initial=False, label=_('I want to receive Wolne Lektury\'s newsletter.'))
    mailing = False
    mailing_field = 'agree_newsletter'
    newsletter = None

    data_processing_part1 = '''\
Administratorem danych osobowych jest Fundacja Nowoczesna Polska (ul. Marszałkowska 84/92 lok. 125, 00-514 Warszawa).
Podanie danych osobowych jest dobrowolne.'''
    data_processing_part2 = '''Dane są przetwarzane w zakresie niezbędnym do wysyłania newslettera odbiorcom.'''
    data_processing_part3 = '''\
Osobom, których dane są zbierane, przysługuje prawo dostępu do treści swoich danych oraz ich poprawiania.
Więcej informacji w <a href="https://nowoczesnapolska.org.pl/prywatnosc/">polityce prywatności.</a>'''

    @property
    def data_processing(self):
        return mark_safe('%s %s %s' % (self.data_processing_part1, self.data_processing_part2, self.data_processing_part3))

    def save(self, *args, **kwargs):
        newsletter = self.newsletter or Newsletter.objects.filter(slug='').first()
        if not newsletter:
            return

        if not (self.mailing or self.cleaned_data.get(self.mailing_field)):
            return
        email = self.cleaned_data[self.email_field]
        try:
            validate_email(email)
        except ValidationError:
            pass
        else:
            subscribe(email, newsletter=newsletter)


class SubscribeForm(NewsletterForm):
    mailing = True
    agree_newsletter = None

    email = EmailField(label=_('email address'))

    def __init__(self, newsletter, *args, **kwargs):
        self.newsletter = newsletter
        super(SubscribeForm, self).__init__(*args, **kwargs)

