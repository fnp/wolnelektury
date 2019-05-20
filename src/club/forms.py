from decimal import Decimal
from django import forms
from . import models
from .payment_methods import method_by_slug, methods
from .payu.forms import CardTokenForm


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = models.Schedule
        fields = ['plan', 'method', 'amount', 'email']
        widgets = {
            'plan': forms.RadioSelect,
            'method': forms.RadioSelect,
        }

    def __init__(self, *args, request=None, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.request = request
        self.plans = models.Plan.objects.all()
        self.payment_methods = methods
        self.fields['amount'].required = False

    def clean(self):
        cleaned_data = super(ScheduleForm, self).clean()

        if 'plan' in cleaned_data:
            cleaned_data['amount'] = self.fields['amount'].clean(
                self.request.POST['amount-{}'.format(cleaned_data['plan'].id)]
            )

            if cleaned_data['amount'] < cleaned_data['plan'].min_amount:
                self.add_error(
                    'amount',
                    'Minimalna kwota dla tego planu to %d zł.' % cleaned_data['plan'].min_amount
                )

        if 'method' in cleaned_data:
            method = method_by_slug[cleaned_data['method']]
            if method not in cleaned_data['plan'].payment_methods():
                self.add_error('method', 'Wybrana metoda płatności nie jest dostępna dla tego planu.')



class PayUCardTokenForm(CardTokenForm):
    def get_queryset(self, view):
        return view.get_schedule().payucardtoken_set
