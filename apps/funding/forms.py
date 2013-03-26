from django import forms
from .models import Offer


class DummyForm(forms.Form):
    amount = forms.DecimalField()
    name = forms.CharField()
    email = forms.EmailField()

    def __init__(self, offer, *args, **kwargs):
        self.offer = offer
        super(DummyForm, self).__init__(*args, **kwargs)

    def clean_amount(self):
        if self.cleaned_data['amount'] <= 0:
            raise forms.ValidationError("A!")
        return self.cleaned_data['amount']

    def clean(self):
        if self.offer != Offer.current():
            raise forms.ValidationError("B!")
        return self.cleaned_data

    def save(self):
        print self.cleaned_data
        return self.offer.fund(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            amount=self.cleaned_data['amount'])

