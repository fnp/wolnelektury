# -*- coding: utf-8 -*-
from django import template
from django.core.cache import cache
from ..models import Chunk, Attachment


register = template.Library()


@register.simple_tag
def chunk(key, cache_time=0):
    try:
        cache_key = 'chunk_' + key
        c = cache.get(cache_key)
        if c is None:
            c = Chunk.objects.get(key=key)
            cache.set(cache_key, c, int(cache_time))
        content = c.content
    except Chunk.DoesNotExist:
        n = Chunk(key=key)
        n.save()
        return ''
    return content


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
