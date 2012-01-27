# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import ugettext_lazy as _

from search.fields import JQueryAutoCompleteSearchField


class SearchForm(forms.Form):
    q = JQueryAutoCompleteSearchField()  # {'minChars': 2, 'selectFirst': True, 'cacheLength': 50, 'matchContains': "word"})

    def __init__(self, source, *args, **kwargs):
        kwargs['auto_id'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget.attrs['id'] = _('search')
        self.fields['q'].widget.attrs['autocomplete'] = 'off'
        self.fields['q'].widget.attrs['data-source'] = source
        if not 'q' in self.data:
            self.fields['q'].widget.attrs['title'] = _('title, author, theme/topic, epoch, kind, genre, phrase')
