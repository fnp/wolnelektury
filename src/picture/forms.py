# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django import forms
from picture.models import Picture


class PictureImportForm(forms.Form):
    picture_xml_file = forms.FileField(required=False)
    picture_xml = forms.CharField(required=False)
    picture_image_file = forms.FileField(required=False)
    picture_image_data = forms.CharField(required=False)

    def clean(self):
        from base64 import b64decode
        from django.core.files.base import ContentFile

        if not self.cleaned_data['picture_xml_file']:
            if self.cleaned_data['picture_xml']:
                self.cleaned_data['picture_xml_file'] = \
                        ContentFile(self.cleaned_data['picture_xml'].encode('utf-8'))
            else:
                raise forms.ValidationError('Proszę dostarczyć XML.')

        if not self.cleaned_data['picture_image_file']:
            if self.cleaned_data['picture_image_data']:
                self.cleaned_data['picture_image_file'] = \
                        ContentFile(b64decode(
                                self.cleaned_data['picture_image_data']))
            else:
                raise forms.ValidationError('Proszę dostarczyć obraz.')

        return super(PictureImportForm, self).clean()

    def save(self, commit=True, **kwargs):
        return Picture.from_xml_file(
            self.cleaned_data['picture_xml_file'], image_file=self.cleaned_data['picture_image_file'],
            overwrite=True, **kwargs)
