# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.forms.widgets import flatatt
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from json import dumps


class JQueryAutoCompleteWidget(forms.TextInput):
    def __init__(self, options, *args, **kwargs):
        self.options = dumps(options)
        super(JQueryAutoCompleteWidget, self).__init__(*args, **kwargs)

    def render_js(self, field_id, options):
        return u'$(\'#%s\').autocomplete(%s).result(autocomplete_result_handler);' % (field_id, options)

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
                'attrs': flatatt(final_attrs),
                'js' : self.render_js(final_attrs['id'], self.options),
            }

        return mark_safe(html)


class JQueryAutoCompleteSearchWidget(JQueryAutoCompleteWidget):
    def __init__(self, *args, **kwargs):
        super(JQueryAutoCompleteSearchWidget, self).__init__(*args, **kwargs)

    def render_js(self, field_id, options):
        return u""
    

class JQueryAutoCompleteField(forms.CharField):
    def __init__(self, source, options={}, *args, **kwargs):
        if 'widget' not in kwargs:
            options['source'] = source
            kwargs['widget'] = JQueryAutoCompleteWidget(options)

        super(JQueryAutoCompleteField, self).__init__(*args, **kwargs)


class JQueryAutoCompleteSearchField(forms.CharField):
    def __init__(self, options={}, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = JQueryAutoCompleteSearchWidget(options)

        super(JQueryAutoCompleteSearchField, self).__init__(*args, **kwargs)
