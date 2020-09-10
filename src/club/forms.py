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
