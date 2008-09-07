# -*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import flatatt
from django.forms.util import smart_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.simplejson import dumps


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
        
        return u'$(\'#%s\').autocomplete(%s%s);' % (field_id, source, options)
    
    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = smart_unicode(value)
        
        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name
        
        html = u'''<input type="text" %(attrs)s/>
            <script type="text/javascript"><!--//
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

