# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from django.core.cache import cache
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from ..models import Chunk, Attachment


register = template.Library()


@register.simple_tag(takes_context=True)
def chunk(context, key, cache_time=0):
    try:
        cache_key = 'chunk:%s:%s' % (key, get_language())
        c = cache.get(cache_key)
        if c is None:
            c = Chunk.objects.get(key=key)
            cache.set(cache_key, c, int(cache_time))
        content = c.content
    except Chunk.DoesNotExist:
        n = Chunk(key=key)
        n.save()
        content = ''

    if context['request'].user.is_staff:
        content = f'<span data-edit="chunks/chunk/{key}"></span>' + content

    return mark_safe(content)


@register.simple_tag
def attachment(key, cache_time=0):
    try:
        cache_key = 'attachment_' + key
        c = cache.get(cache_key)
        if c is None:
            c = Attachment.objects.get(key=key)
            cache.set(cache_key, c, int(cache_time))
        return c.attachment.url
    except Attachment.DoesNotExist:
        return ''
