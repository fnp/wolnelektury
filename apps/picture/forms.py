from django import forms
from django.utils.translation import ugettext_lazy as _
from picture.models import Picture


class PictureImportForm(forms.Form):
    picture_xml_file = forms.FileField(required=False)
    picture_xml = forms.CharField(required=False)
    picture_image_file = forms.FileField(required=True)

    def clean(self):
        from django.core.files.base import ContentFile

        if not self.cleaned_data['picture_xml_file']:
            if self.cleaned_data['picture_xml']:
                self.cleaned_data['picture_xml_file'] = \
                        ContentFile(self.cleaned_data['picture_xml'].encode('utf-8'))
            else:
                raise forms.ValidationError(_("Please supply an XML."))
        return super(PictureImportForm, self).clean()

    def save(self, commit=True, **kwargs):
        return Picture.from_xml_file(self.cleaned_data['picture_xml_file'], image_file=self.cleaned_data['picture_image_file'],
                                     overwrite=True, **kwargs)
