# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import ugettext_lazy as _

class SuggestForm(forms.Form):
    author = forms.CharField(label=_('Author'), max_length=50, required=False)
    email = forms.EmailField(label=_('E-mail'), required=False)
    title = forms.CharField(label=_('Title'), max_length=120, required=True)
    description = forms.CharField(label=_('Description'), widget=forms.Textarea, required=True)
