# -*- coding: utf-8
from django import forms
from . import models
from . import widgets
from .payment_methods import method_by_slug 


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = models.Schedule
        fields = ['plan', 'method', 'amount', 'email']
        widgets = {
            'plan': forms.RadioSelect,
            'method': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.fields['plan'].empty_label = None

    def clean(self):
        cleaned_data = super(ScheduleForm, self).clean()
        if 'method' in cleaned_data:
            method = method_by_slug[cleaned_data['method']]
            if method not in cleaned_data['plan'].payment_methods():
                self.add_error('method', 'Metoda płatności niedostępna dla tego planu.')
        if cleaned_data['amount'] < cleaned_data['plan'].min_amount:
            self.add_error('amount', 'Minimalna kwota dla tego planu to %d zł.' % cleaned_data['plan'].min_amount)

