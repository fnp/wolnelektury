# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _
from slughifi import slughifi

from catalogue.models import Tag, Book
from catalogue.fields import JQueryAutoCompleteSearchField
from catalogue import utils


class BookImportForm(forms.Form):
    book_xml_file = forms.FileField(required=False)
    book_xml = forms.CharField(required=False)

    def clean(self):
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
    q = JQueryAutoCompleteSearchField('/newsearch/hint/') # {'minChars': 2, 'selectFirst': True, 'cacheLength': 50, 'matchContains': "word"})
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
            choices=[(tag.id, "%s (%s)" % (tag.name, tag.get_count())) for tag in Tag.objects.filter(category='set', user=user)],
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


FORMATS = (
    ('mp3', 'MP3'),
    ('ogg', 'OGG'),
    ('pdf', 'PDF'),
    ('odt', 'ODT'),
    ('txt', 'TXT'),
    ('epub', 'EPUB'),
    ('daisy', 'DAISY'),
    ('mobi', 'MOBI'),
)


class DownloadFormatsForm(forms.Form):
    formats = forms.MultipleChoiceField(required=False, choices=FORMATS, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
         super(DownloadFormatsForm, self).__init__(*args, **kwargs)

