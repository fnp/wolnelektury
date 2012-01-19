# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import datetime

from django.conf import settings
from django.db import models
from django.db.models.fields.files import FieldFile
from django import forms
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        return json.JSONEncoder.default(self, obj)


def dumps(data):
    return JSONEncoder().encode(data)


def loads(str):
    return json.loads(str, encoding=settings.DEFAULT_CHARSET)


class JSONFormField(forms.CharField):
    widget = forms.Textarea

    def clean(self, value):
        try:
            loads(value)
            return value
        except ValueError, e:
            raise forms.ValidationError(_('Enter a valid JSON value. Error: %s') % e)


class JSONField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {'form_class': JSONFormField}
        defaults.update(kwargs)
        return super(JSONField, self).formfield(**defaults)

    def db_type(self, connection):
        return 'text'

    def get_internal_type(self):
        return 'TextField'

    def contribute_to_class(self, cls, name):
        super(JSONField, self).contribute_to_class(cls, name)

        def get_value(model_instance):
            return loads(getattr(model_instance, self.attname, None))
        setattr(cls, 'get_%s_value' % self.name, get_value)

        def set_value(model_instance, json):
            return setattr(model_instance, self.attname, dumps(json))
        setattr(cls, 'set_%s_value' % self.name, set_value)


class OverwritingFieldFile(FieldFile):
    """
        Deletes the old file before saving the new one.
    """

    def save(self, name, content, *args, **kwargs):
        leave = kwargs.pop('leave', None)
        # delete if there's a file already and there's a new one coming
        if not leave and self and (not hasattr(content, 'path') or
                                   content.path != self.path):
            self.delete(save=False)
        return super(OverwritingFieldFile, self).save(
                name, content, *args, **kwargs)


class OverwritingFileField(models.FileField):
    attr_class = OverwritingFieldFile


try:
    # check for south
    from south.modelsinspector import add_introspection_rules

    add_introspection_rules([], ["^catalogue\.fields\.JSONField"])
    add_introspection_rules([], ["^catalogue\.fields\.OverwritingFileField"])
except ImportError:
    pass
