# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from django.utils.http import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def set_get(context, *omit, **kwargs):
    request = context['request']
    query = request.GET.dict()
    for k in omit:
        if k in query:
            del query[k]
    for k, v in kwargs.items():
        query[k] = v
    return urlencode(query)
