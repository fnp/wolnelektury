# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django import template
from django.core.cache import cache
from django.utils.safestring import mark_safe
from sponsors.models import SponsorPage


register = template.Library()


@register.simple_tag
def sponsor_page(name):
    key = 'sponsor_page:' + name
    content = cache.get(key)
    if content is None:
        try:
            page = SponsorPage.objects.get(name=name)
        except SponsorPage.DoesNotExist:
            content = ''
        else:
            content = page.html
        cache.set(key, content) 
    return mark_safe(content)
