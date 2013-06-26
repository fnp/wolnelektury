from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext as __, get_language
from .models import Funding
from .widgets import PerksAmountWidget


class FundingForm(forms.Form):
    required_css_class = 'required'

    amount = forms.DecimalField(label=_("Amount"), decimal_places=2,
        widget=PerksAmountWidget())
    name = forms.CharField(label=_("Name"), required=False,
        help_text=_("Optional name for public list of contributors"))
    email = forms.EmailField(label=_("Contact e-mail"),
        help_text=_("We'll use it to contact you about your perks and fundraiser status and payment updates.<br/> "
            "Won't be publicised."), required=False)

    def __init__(self, offer, *args, **kwargs):
        self.offer = offer
        super(FundingForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.form_instance = self

    def clean_amount(self):
        if self.cleaned_data['amount'] <= 0:
            raise forms.ValidationError(__("Enter positive amount."))
        return self.cleaned_data['amount']

    def clean(self):
        if not self.offer.is_current():
            raise forms.ValidationError(__("This offer is out of date."))
        return self.cleaned_data

    def save(self):
        funding = Funding.objects.create(
            offer=self.offer,
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            amount=self.cleaned_data['amount'],
            language_code = get_language(),
        )
        funding.perks = funding.offer.get_perks(funding.amount)
        return funding

