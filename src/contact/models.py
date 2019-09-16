# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
import yaml
from hashlib import sha1
from django.db import models
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from . import app_settings


class Contact(models.Model):
    created_at = models.DateTimeField(_('submission date'), auto_now_add=True)
    ip = models.GenericIPAddressField(_('IP address'))
    contact = models.EmailField(_('contact'), max_length=128)
    form_tag = models.CharField(_('form'), max_length=32, db_index=True)
    body = models.TextField(_('body'))

    @staticmethod
    def pretty_print(value, for_html=False):
        if type(value) in (tuple, list, dict):
            value = yaml.safe_dump(value, allow_unicode=True, default_flow_style=False)
            if for_html:
                value = smart_text(value).replace(" ", chr(160))
        return value

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('submitted form')
        verbose_name_plural = _('submitted forms')

    def __str__(self):
        return str(self.created_at)

    def digest(self):
        serialized_body = ';'.join(sorted('%s:%s' % item for item in self.get_body_json().items()))
        data = '%s%s%s%s%s' % (self.id, self.contact, serialized_body, self.ip, self.form_tag)
        return sha1(data).hexdigest()

    def keys(self):
        try:
            from .views import contact_forms
            orig_fields = contact_forms[self.form_tag]().fields
        except KeyError:
            orig_fields = {}
        return list(orig_fields.keys())

    def items(self):
        body = self.get_body_json()
        return [(key, body[key]) for key in self.keys() if key in body]

    def get_body_json(self):
        return json.loads(self.body or '{}')


class Attachment(models.Model):
    contact = models.ForeignKey(Contact, models.CASCADE)
    tag = models.CharField(max_length=64)
    file = models.FileField(upload_to='contact/attachment')

    def get_absolute_url(self):
        return reverse('contact_attachment', args=[self.contact_id, self.tag])


__import__(app_settings.FORMS_MODULE)
