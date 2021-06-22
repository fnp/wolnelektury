# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from decimal import Decimal
from django import forms
from django.utils.translation import ugettext as _
from newsletter.forms import NewsletterForm
from . import models, payment_methods
from .payu.forms import CardTokenForm


class ScheduleForm(forms.ModelForm, NewsletterForm):
    data_processing = '''Administratorem danych osobowych jest Fundacja Nowoczesna Polska (ul. Marszałkowska 84/92 lok. 125, 00-514 Warszawa). Podanie danych osobowych jest dobrowolne, ale konieczne do przeprowadzenia wpłaty. Dane są przetwarzane w zakresie niezbędnym do zaksięgowania darowizny i przekazywania Tobie powiadomień dotyczących wpłaty, a także wysyłania Tobie wiadomości mailowych promujących zbiórki i inne formy wsparcia Fundacji. W przypadku wyrażenia dodatkowej zgody adres e-mail zostanie wykorzystany także w zakresie niezbędnym do wysyłania newslettera odbiorcom. Osobom, których dane są zbierane, przysługuje prawo dostępu do treści swoich danych oraz ich poprawiania.'''

    class Meta:
        model = models.Schedule
        fields = ['monthly', 'amount', 'email', 'method']
        widgets = {
            'amount': forms.HiddenInput,
            'monthly': forms.HiddenInput,
            'method': forms.HiddenInput,
        }

    def __init__(self, referer=None, **kwargs):
        self.referer = referer
        super().__init__(**kwargs)

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

    def clean_method(self):
        value = self.cleaned_data['method']
        monthly = self.cleaned_data['monthly']
        for m in payment_methods.methods:
            if m.slug == value:
                if (monthly and m.is_recurring) or (not monthly and m.is_onetime):
                    return value
        if monthly:
            return payment_methods.recurring_payment_method.slug
        else:
            return payment_methods.single_payment_method.slug
    
    def save(self, *args, **kwargs):
        NewsletterForm.save(self, *args, **kwargs)
        self.instance.source = self.referer or ''
        return super().save(*args, **kwargs)


class PayUCardTokenForm(CardTokenForm):
    def get_queryset(self, view):
        return view.get_schedule().payucardtoken_set
