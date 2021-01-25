# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from decimal import Decimal
from django import forms
from django.utils.translation import ugettext as _
from newsletter.forms import NewsletterForm
from . import models
from .payu.forms import CardTokenForm


class ScheduleForm(forms.ModelForm, NewsletterForm):
    data_processing = '''Administratorem danych osobowych jest Fundacja Nowoczesna Polska (ul. Marszałkowska 84/92 lok. 125, 00-514 Warszawa). Podanie danych osobowych jest dobrowolne, ale konieczne do przeprowadzenia wpłaty. Dane są przetwarzane w zakresie niezbędnym do zaksięgowania darowizny i przekazywania Tobie powiadomień dotyczących wpłaty, a także wysyłania Tobie wiadomości mailowych promujących zbiórki i inne formy wsparcia Fundacji. W przypadku wyrażenia dodatkowej zgody adres e-mail zostanie wykorzystany także w zakresie niezbędnym do wysyłania newslettera odbiorcom. Osobom, których dane są zbierane, przysługuje prawo dostępu do treści swoich danych oraz ich poprawiania.'''

    class Meta:
        model = models.Schedule
        fields = ['monthly', 'amount', 'email']
        widgets = {
            'amount': forms.HiddenInput,
            'monthly': forms.HiddenInput,
        }

    def clean_amount(self):
        value = self.cleaned_data['amount']
        club = models.Club.objects.first()
        if club and value < club.min_amount:
            raise forms.ValidationError(
                _('Minimal amount is %(amount)d PLN.') % {
                    'amount': club.min_amount
                }
            )
        return value

    def save(self, *args, **kwargs):
        NewsletterForm.save(self, *args, **kwargs)
        return super().save(*args, **kwargs)


class PayUCardTokenForm(CardTokenForm):
    def get_queryset(self, view):
        return view.get_schedule().payucardtoken_set
