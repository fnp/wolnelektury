# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import datetime

from django.conf import settings
from django.db import models
from django.db.models import signals
from django import forms
from django.forms.widgets import flatatt
from django.forms.util import smart_unicode
from django.utils import simplejson as json
from django.utils.html import escape
from django.utils.safestring import mark_safe


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

    def db_type(self):
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


class JQueryAutoCompleteWidget(forms.TextInput):
    def __init__(self, source, options=None, *args, **kwargs):
        self.source = source
        self.options = None
        if options:
            self.options = dumps(options)
        super(JQueryAutoCompleteWidget, self).__init__(*args, **kwargs)
    
    def render_js(self, field_id):
        source = "'%s'" % escape(self.source)
        options = ''
        if self.options:
            options += ', %s' % self.options
        
        return u'$(\'#%s\').autocomplete(%s%s).result(autocomplete_result_handler);' % (field_id, source, options)
    
    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = smart_unicode(value)
        
        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name
        
        html = u'''<input type="text" %(attrs)s/>
            <script type="text/javascript">//<!--
            %(js)s//--></script>
            ''' % {
                'attrs' : flatatt(final_attrs),
                'js' : self.render_js(final_attrs['id']),
            }
        
        return mark_safe(html)


class JQueryAutoCompleteField(forms.CharField):
    def __init__(self, source, options=None, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = JQueryAutoCompleteWidget(source, options)
        
        super(JQueryAutoCompleteField, self).__init__(*args, **kwargs)

