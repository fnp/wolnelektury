# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import gettext_lazy as _


class PaypalSubscriptionForm(forms.Form):
    amount = forms.IntegerField(min_value=5, max_value=30000, initial=20, label=_('amount in PLN'))
