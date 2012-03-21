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


PDF_PAGE_SIZES = (
    ('a4paper', _('A4')),
    ('a5paper', _('A5')),
)


PDF_LEADINGS = (
    ('', _('Normal leading')),
    ('onehalfleading', _('One and a half leading')),
    ('doubleleading', _('Double leading')),
    )

PDF_FONT_SIZES = (
    ('11pt', _('Default')),
    ('13pt', _('Big'))
    )


class CustomPDFForm(forms.Form):
    nofootnotes = forms.BooleanField(required=False, label=_("Don't show footnotes"))
    nothemes = forms.BooleanField(required=False, label=_("Don't disply themes"))
    nowlfont = forms.BooleanField(required=False, label=_("Don't use our custom font"))
    ##    pagesize = forms.ChoiceField(PDF_PAGE_SIZES, required=True, label=_("Paper size"))
    leading = forms.ChoiceField(PDF_LEADINGS, required=False, label=_("Leading"))
    fontsize = forms.ChoiceField(PDF_FONT_SIZES, required=True, label=_("Font size"))

    @property
    def customizations(self):
        c = []
        if self.cleaned_data['nofootnotes']:
            c.append('nofootnotes')
            
        if self.cleaned_data['nothemes']:
            c.append('nothemes')
            
        if self.cleaned_data['nowlfont']:
            c.append('nowlfont')
        
            ##  c.append(self.cleaned_data['pagesize'])
        c.append(self.cleaned_data['fontsize'])

        if self.cleaned_data['leading']:
            c.append(self.cleaned_data['leading'])

        c.sort()

        return c

