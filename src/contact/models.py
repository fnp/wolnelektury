# -*- coding: utf-8 -*-
import yaml
from hashlib import sha1
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from . import app_settings


class Contact(models.Model):
    created_at = models.DateTimeField(_('submission date'), auto_now_add=True)
    ip = models.GenericIPAddressField(_('IP address'))
    contact = models.EmailField(_('contact'), max_length=128)
    form_tag = models.CharField(_('form'), max_length=32, db_index=True)
    body = JSONField(_('body'))

    @staticmethod
    def pretty_print(value, for_html=False):
        if type(value) in (tuple, list, dict):
            value = yaml.safe_dump(value, allow_unicode=True, default_flow_style=False)
            if for_html:
                value = smart_unicode(value).replace(u" ", unichr(160))
        return value

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('submitted form')
        verbose_name_plural = _('submitted forms')

    def __unicode__(self):
        return unicode(self.created_at)

    def digest(self):
        serialized_body = ';'.join(sorted('%s:%s' % item for item in self.body.iteritems()))
        data = '%s%s%s%s%s' % (self.id, self.contact, serialized_body, self.ip, self.form_tag)
        return sha1(data).hexdigest()


class Attachment(models.Model):
    contact = models.ForeignKey(Contact)
    tag = models.CharField(max_length=64)
    file = models.FileField(upload_to='contact/attachment')

    @models.permalink
    def get_absolute_url(self):
        return 'contact_attachment', [self.contact_id, self.tag]


__import__(app_settings.FORMS_MODULE)
