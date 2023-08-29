# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from decimal import Decimal
from django import forms
from newsletter.forms import NewsletterForm
from . import models, payment_methods
from .payu.forms import CardTokenForm


class PayUCardTokenForm(CardTokenForm):
    def get_queryset(self, view):
        return view.get_schedule().payucardtoken_set



class DonationStep1Form(forms.ModelForm):
    switch = forms.CharField()
    single_amount = forms.IntegerField(required=False)
    monthly_amount = forms.IntegerField(required=False)
    single_amount_selected = forms.IntegerField(required=False)
    monthly_amount_selected = forms.IntegerField(required=False)
    custom_amount = forms.IntegerField(required=False)

    amount = forms.IntegerField(required=False) # hidden

    class Meta:
        model = models.Schedule
        fields = [
            'amount',
            'monthly'
            ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        club = models.Club.objects.first()
        if club is not None:
            self.fields['custom_amount'].widget.attrs['min'] = club.min_amount

    def clean(self):
        state = {}
        state['monthly'] = self.cleaned_data['switch'] == 'monthly'
        which = 'monthly' if state['monthly'] else 'single'
        state['amount'] = \
            self.cleaned_data[f'{which}_amount'] or \
            self.cleaned_data['custom_amount'] or \
            self.cleaned_data[f'{which}_amount_selected']

        return state



class DonationStep2Form(forms.ModelForm, NewsletterForm):
    class Meta:
        model = models.Schedule
        fields = [
            'first_name', 'last_name',
            'email', 'phone',
            'postal',
            'postal_code', 'postal_town', 'postal_country',
            ]
        widgets = {
            'amount': forms.HiddenInput,
            'monthly': forms.HiddenInput,
        }
    
    def __init__(self, referer=None, **kwargs):
        self.referer = referer
        super().__init__(**kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone'].required = True
        
        self.consent = []
        for c in models.Consent.objects.filter(active=True).order_by('order'):
            key = f'consent{c.id}'
            self.fields[key] = forms.BooleanField(
                label=c.text,
                required=c.required
            )
            self.consent.append((
                c, key, (lambda k: lambda: self[k])(key)
            ))



    def save(self, *args, **kwargs):
        NewsletterForm.save(self, *args, **kwargs)
        self.instance.source = self.referer or ''
        instance = super().save(*args, **kwargs)

        consents = []
        for consent, key, consent_field in self.consent:
            if self.cleaned_data[key]:
                instance.consent.add(consent)

        return instance

