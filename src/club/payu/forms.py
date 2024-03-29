# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django import forms


class CardTokenForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput)

    def get_queryset(self, view):
        raise NotImplementedError()

    def save(self, view):
        self.instance, created = self.get_queryset(view).get_or_create(
            pos_id=view.get_pos().pos_id,
            disposable_token=self.cleaned_data['token']
        )
