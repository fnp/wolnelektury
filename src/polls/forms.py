# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django import forms


class PollForm(forms.Form):
    vote = forms.ChoiceField(widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        poll = kwargs.pop('poll', None)
        super(PollForm, self).__init__(*args, **kwargs)
        self.fields['vote'].choices = [(item.id, item.content) for item in poll.items.all()]
