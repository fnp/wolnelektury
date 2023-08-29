# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from datetime import date
import json
from urllib.request import urlopen

from django import forms
from slugify import slugify

from isbn.management.commands.import_onix import UNKNOWN
from isbn.models import ONIXRecord, ISBNPool
from isbn.utils import isbn_data, PRODUCT_FORMS, PRODUCT_FORM_DETAILS
from librarian.parser import WLDocument


class WLISBNForm(forms.Form):
    platform_url = forms.URLField(label='Adres na platformie')
    publishing_date = forms.DateField(label='Data publikacji', initial=date.today)

    def prepare_data(self):
        platform_url = self.cleaned_data['platform_url']
        platform_slug = platform_url.strip('/').split('/')[-1]
        xml_url = 'https://redakcja.wolnelektury.pl/documents/book/%s/xml' % platform_slug
        doc = WLDocument.from_file(urlopen(xml_url))
        data = isbn_data(doc)
        data['publishing_date'] = self.cleaned_data['publishing_date']
        return data


class WLConfirmForm(WLISBNForm):
    platform_url = forms.URLField(widget=forms.HiddenInput)
    publishing_date = forms.DateField(widget=forms.HiddenInput)

    @staticmethod
    def contributors(data):
        person_name = data['name']
        corporate_name = data['corporate_name']
        if person_name:
            # assuming that unknown can't be a co-author
            if person_name == UNKNOWN:
                return [{'role': 'A01', 'unnamed': '01'}]
            else:
                return [{'role': 'A01', 'name': name} for name in person_name.split('; ')]
        if corporate_name:
            return [{'role': 'A01', 'corporate_name': name} for name in corporate_name.split('; ')]

    def save(self):
        data = self.prepare_data()
        for file_format in data['formats']:
            data['product_form'] = PRODUCT_FORMS[file_format]
            data['product_form_detail'] = PRODUCT_FORM_DETAILS[file_format]
            data['contributors'] = json.dumps(self.contributors(data))
            ONIXRecord.new_record(purpose=ISBNPool.PURPOSE_WL, data=data)
        return data


class FNPISBNForm(forms.Form):
    FORMAT_CHOICES = (
        ('HTML', 'HTML'),
        ('PDF', 'PDF'),
        ('EPUB', 'ePUB'),
        ('MOBI', 'MOBI'),
        ('TXT', 'TXT'),
        ('SOFT', 'Miękka oprawa'),
    )
    LANGUAGE_CHOICES = (
        ('pol', 'polski'),
        ('eng', 'angielski'),
        ('ger', 'niemiecki'),
        ('fre', 'francuski'),
    )

    title = forms.CharField()
    authors = forms.CharField(help_text='wartości oddzielone przecinkami lub „Wielu autorów”')
    formats = forms.MultipleChoiceField(choices=FORMAT_CHOICES)
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES)
    publishing_date = forms.DateField()

    def prepare_author(self, name):
        if name == 'Wielu autorów':
            return {'role': 'A01', 'unnamed': '04'}
        if ' ' in name:
            first_name, last_name = [s.strip() for s in name.rsplit(' ', 1)]
            output_name = '%s, %s' % (last_name, first_name)
        else:
            output_name = name.strip()
        return {'role': 'A01', 'name': output_name}

    def slug(self):
        return slugify('fnp %s %s' % (self.cleaned_data['authors'], self.cleaned_data['title']))

    def save(self):
        data = {
            'title': self.cleaned_data['title'],
            'language': self.cleaned_data['language'],
            'publishing_date': self.cleaned_data['publishing_date'],
            'contributors': json.dumps([self.prepare_author(a) for a in self.cleaned_data['authors'].split(',')]),
            'edition_type': 'NED',
            'imprint': 'Fundacja Nowoczesna Polska',
            'dc_slug': self.slug(),
        }
        formats = self.cleaned_data['formats']
        for book_format in formats:
            data['product_form'] = PRODUCT_FORMS[book_format]
            if book_format in PRODUCT_FORM_DETAILS:
                data['product_form_detail'] = PRODUCT_FORM_DETAILS[book_format]
            else:
                del data['product_form_detail']
            ONIXRecord.new_record('FNP', data)
