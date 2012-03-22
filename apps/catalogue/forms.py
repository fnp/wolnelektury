# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import ugettext_lazy as _

from catalogue.models import Book


class BookImportForm(forms.Form):
    book_xml_file = forms.FileField(required=False)
    book_xml = forms.CharField(required=False)

    def clean(self):
        from django.core.files.base import ContentFile

        if not self.cleaned_data['book_xml_file']:
            if self.cleaned_data['book_xml']:
                self.cleaned_data['book_xml_file'] = \
                        ContentFile(self.cleaned_data['book_xml'].encode('utf-8'))
            else:
                raise forms.ValidationError(_("Please supply an XML."))
        return super(BookImportForm, self).clean()

    def save(self, commit=True, **kwargs):
        return Book.from_xml_file(self.cleaned_data['book_xml_file'], overwrite=True, **kwargs)


FORMATS = [(f, f.upper()) for f in Book.ebook_formats]


class DownloadFormatsForm(forms.Form):
    formats = forms.MultipleChoiceField(required=False, choices=FORMATS,
            widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(DownloadFormatsForm, self).__init__(*args, **kwargs)


CUSTOMIZATION_FLAGS = (
    ('nofootnotes', _("Don't show footnotes")),
    ('nothemes', _("Don't disply themes")),
    ('nowlfont', _("Don't use our custom font")),
    )
CUSTOMIZATION_OPTIONS = (
    ('leading', _("Leading"), (
        ('defaultleading', _('Normal leading')),
        ('onehalfleading', _('One and a half leading')),
        ('doubleleading', _('Double leading')),
        )),
    ('fontsize', _("Font size"), (
        ('11pt', _('Default')),
        ('13pt', _('Big'))
        )),
#    ('pagesize', _("Paper size"), (
#        ('a4paper', _('A4')),
#        ('a5paper', _('A5')),
#        )),
    )


class CustomPDFForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CustomPDFForm, self).__init__(*args, **kwargs)
        for name, label in CUSTOMIZATION_FLAGS:
            self.fields[name] = forms.BooleanField(required=False, label=label)
        for name, label, choices in CUSTOMIZATION_OPTIONS:
            self.fields[name] = forms.ChoiceField(choices, label=label)

    @property
    def customizations(self):
        c = []
        for name, label in CUSTOMIZATION_FLAGS:
            if self.cleaned_data.get(name):
                c.append(name)
        for name, label, choices in CUSTOMIZATION_OPTIONS:
            c.append(self.cleaned_data[name])
        c.sort()
        return c
