from django import template
from django.utils.safestring import mark_safe

from sponsors import models


register = template.Library()


def sponsor_page(name):
    try:
        page = models.SponsorPage.objects.get(name=name)
    except:
        return u''
    return mark_safe(page.html)
    
sponsor_page = register.simple_tag(sponsor_page)
