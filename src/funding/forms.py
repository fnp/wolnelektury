# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django import forms
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext, get_language

from newsletter.forms import NewsletterForm
from club.payment_methods import PayU
from .models import Funding
from .widgets import PerksAmountWidget
from . import app_settings


payment_method = PayU(app_settings.PAYU_POS)


class FundingForm(NewsletterForm):
    required_css_class = 'required'

    amount = forms.DecimalField(label=_("Kwota"), decimal_places=2, widget=PerksAmountWidget())
    name = forms.CharField(
        label=_("Imię i nazwisko na listę darczyńców"),
        required=False,
        help_text=_("Opcjonalnie imię i nazwisko lub pseudonim do publicznej listy darczyńców.")
    )
    email = forms.EmailField(
        label=_("E-mail kontaktowy"),
        help_text=mark_safe(_(
            "Użyjemy go do informowania Cię o zmianach statusu płatności i zbiórki "
            "(z czego zawsze możesz zrezygnować).<br/>"
            "Twój adres e-mail nie będzie upubliczniony.")),
        required=False)

    data_processing_part2 = _('''\
W przypadku podania danych zostaną one wykorzystane w sposób podany powyżej, a w przypadku wyrażenia dodatkowej zgody 
adres e-mail zostanie wykorzystany także w celu przesyłania newslettera Wolnych Lektur.''')

    def __init__(self, request, offer, *args, **kwargs):
        self.offer = offer
        self.user = request.user if request.user.is_authenticated else None
        self.client_ip = request.META['REMOTE_ADDR']
        super(FundingForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.form_instance = self

    def clean_amount(self):
        if self.cleaned_data['amount'] < app_settings.MIN_AMOUNT:
            min_amount = app_settings.MIN_AMOUNT
            if isinstance(min_amount, float):
                min_amount = formats.number_format(min_amount, 2)
            raise forms.ValidationError(
                gettext("Minimalna kwota wpłaty to %(amount)s zł.") % {
                    'amount': min_amount})
        return self.cleaned_data['amount']

    def clean(self):
        if not self.offer.is_current():
            raise forms.ValidationError(gettext("Ta zbiórka jest już nieaktywna."))
        return self.cleaned_data

    def save(self):
        super(FundingForm, self).save()
        funding = Funding.objects.create(
            offer=self.offer,
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            amount=self.cleaned_data['amount'],
            language_code=get_language(),
            user=self.user,
            pos_id=payment_method.pos_id,
            customer_ip=self.client_ip,
        )
        funding.perks.set(funding.offer.get_perks(funding.amount))
        return funding
