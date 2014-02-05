from django import template
from django.db import models
from django.core.cache import cache


register = template.Library()

Chunk = models.get_model('chunks', 'chunk')
Attachment = models.get_model('chunks', 'attachment')


@register.simple_tag
def chunk(key, cache_time=0):
    try:
        cache_key = Chunk.cache_key(key)
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
