# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import ugettext_lazy as _
from slughifi import slughifi

from catalogue.models import Tag, Book
from catalogue.fields import JQueryAutoCompleteField
from catalogue import utils


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


class SearchForm(forms.Form):
    q = JQueryAutoCompleteField('/katalog/tags/', {'minChars': 2, 'selectFirst': True, 'cacheLength': 50, 'matchContains': "word"})
    tags = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        tags = kwargs.pop('tags', [])
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget.attrs['title'] = _('title, author, theme/topic, epoch, kind, genre')
	    #self.fields['q'].widget.attrs['style'] = ''
        self.fields['tags'].initial = '/'.join(tag.url_chunk for tag in Tag.get_tag_list(tags))


class UserSetsForm(forms.Form):
    def __init__(self, book, user, *args, **kwargs):
        super(UserSetsForm, self).__init__(*args, **kwargs)
        self.fields['set_ids'] = forms.ChoiceField(
            choices=[(tag.id, tag.name) for tag in Tag.objects.filter(category='set', user=user)],
        )


class ObjectSetsForm(forms.Form):
    def __init__(self, obj, user, *args, **kwargs):
        super(ObjectSetsForm, self).__init__(*args, **kwargs)
        self.fields['set_ids'] = forms.MultipleChoiceField(
            label=_('Shelves'),
            required=False,
            choices=[(tag.id, "%s (%s)" % (tag.name, tag.book_count)) for tag in Tag.objects.filter(category='set', user=user)],
            initial=[tag.id for tag in obj.tags.filter(category='set', user=user)],
            widget=forms.CheckboxSelectMultiple
        )


class NewSetForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)

    def __init__(self, *args, **kwargs):
        super(NewSetForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['title'] = _('Name of the new shelf')

    def save(self, user, commit=True):
        name = self.cleaned_data['name']
        new_set = Tag(name=name, slug=utils.get_random_hash(name), sort_key=name.lower(),
            category='set', user=user)

        new_set.save()
        return new_set


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

