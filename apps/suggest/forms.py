# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import ugettext_lazy as _

class SuggestForm(forms.Form):
    contact = forms.CharField(label=_('Contact'), max_length=120, required=False)
    description = forms.CharField(label=_('Description'), widget=forms.Textarea, required=True)
