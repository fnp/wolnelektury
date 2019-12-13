from django import template
from ..models import Banner
from ..places import PLACES


register = template.Library()


@register.inclusion_tag('annoy/banner.html', takes_context=True)
def annoy_banner(context, place):
    banners = Banner.choice(place, request=context['request'])
    return {
        'banner': banners.first(),
        'closable': PLACES.get(place, False),
    }


@register.inclusion_tag('annoy/banners.html', takes_context=True)
def annoy_banners(context, place):
    return {
        'banners': Banner.choice(place, request=context['request']),
        'closable': PLACES.get(place, False),
    }
