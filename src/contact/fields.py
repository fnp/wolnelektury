# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from .widgets import HeaderWidget


class HeaderField(forms.CharField):
    def __init__(self, required=False, widget=None, *args, **kwargs):
        if widget is None:
            widget = HeaderWidget
        super(HeaderField, self).__init__(required=required, widget=widget, *args, **kwargs)
