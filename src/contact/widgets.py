# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.forms.utils import flatatt
from django.utils.html import format_html


class HeaderWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None):
        attrs.update(self.attrs)
        return format_html('<a{0}></a>', flatatt(attrs))
