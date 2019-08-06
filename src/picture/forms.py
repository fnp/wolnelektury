# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import ugettext_lazy as _
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
                raise forms.ValidationError(_("Please supply an XML."))

        if not self.cleaned_data['picture_image_file']:
            if self.cleaned_data['picture_image_data']:
                self.cleaned_data['picture_image_file'] = \
                        ContentFile(b64decode(
                                self.cleaned_data['picture_image_data']))
            else:
                raise forms.ValidationError(_("Please supply an image."))

        return super(PictureImportForm, self).clean()

    def save(self, commit=True, **kwargs):
        return Picture.from_xml_file(
            self.cleaned_data['picture_xml_file'], image_file=self.cleaned_data['picture_image_file'],
            overwrite=True, **kwargs)
