# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from re import split

from django import template

register = template.Library()


"""
In template:
    {% set_get_paramater param1='const_value',param2=,param3=variable %}
results with changes to query string:
    param1 is set to `const_value' string
    param2 is unset, if exists,
    param3 is set to the value of variable in context

Using 'django.core.context_processors.request' is required.

"""


class SetGetParameter(template.Node):
    def __init__(self, values):
        self.values = values
        
    def render(self, context):
        request = template.Variable('request').resolve(context)
        params = request.GET.copy()
        for key, value in self.values.items():
            if value == '':
                if key in params:
                    del(params[key])
            else:
                params[key] = template.Variable(value).resolve(context)
        return '?%s' %  params.urlencode()


@register.tag
def set_get_parameter(parser, token):
    parts = split(r'\s+', token.contents, 2)

    values = {}
    for pair in parts[1].split(','):
        s = pair.split('=')
        values[s[0]] = s[1]

    return SetGetParameter(values)
