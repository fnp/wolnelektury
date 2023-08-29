# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django import forms
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from .widgets import HeaderWidget


class HeaderField(forms.CharField):
    def __init__(self, required=False, widget=None, *args, **kwargs):
        if widget is None:
            widget = HeaderWidget
        super(HeaderField, self).__init__(required=False, widget=widget, *args, **kwargs)
        self.label = mark_safe('<b>' + conditional_escape(self.label) + '</b>')
        self.label_suffix = ''


class SeparatorField(HeaderField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = ''
