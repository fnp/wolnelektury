from django import template
from ..models import Banner
from ..places import PLACES


register = template.Library()


@register.inclusion_tag('annoy/banner.html', takes_context=True)
def annoy_banner(context, place, **kwargs):
    banners = Banner.choice(place, request=context['request'], **kwargs)
    return {
        'banner': banners.first(),
        'closable': PLACES.get(place, False),
    }

@register.inclusion_tag('annoy/banner_blackout.html', takes_context=True)
def annoy_banner_blackout(context):
    banners = Banner.choice('blackout', request=context['request'])
    return {
        'banner': banners.first(),
        'closable': True,
    }

@register.inclusion_tag('annoy/banner_top.html', takes_context=True)
def annoy_banner_top(context):
    banners = Banner.choice('top', request=context['request'])
    return {
        'banner': banners.first(),
        'closable': True,
    }

@register.inclusion_tag('annoy/banners.html', takes_context=True)
def annoy_banners(context, place):
    return {
        'banners': Banner.choice(place, request=context['request']),
        'closable': PLACES.get(place, False),
    }


@register.inclusion_tag('annoy/banner_crisis.html', takes_context=True)
def annoy_banner_crisis(context):
    banners = Banner.choice('crisis', request=context['request'], exemptions=False)
    return {
        'banner': banners.first(),
        'closable': True,
    }

@register.inclusion_tag('annoy/banner_seasonal.html', takes_context=True)
def annoy_banner_seasonal(context):
    banners = Banner.choice('seasonal', request=context['request'], exemptions=False)
    return {
        'banner': banners.first(),
        'closable': False,
    }

@register.inclusion_tag('annoy/banner_seasonal_overlay.html', takes_context=True)
def annoy_banner_seasonal_overlay(context):
    banners = Banner.choice('seasonal-overlay', request=context['request'])
    return {
        'banner': banners.first(),
    }


@register.simple_tag(takes_context=True)
def seasonal_overlay_exists(context):
    return Banner.choice('seasonal-overlay', request=context['request'], exemptions=False).exists()


@register.inclusion_tag('annoy/checkout_header.html', takes_context=True)
def annoy_checkout_header(context):
    banners = Banner.choice('seasonal-overlay', request=context['request'], exemptions=False)
    return {
        'banner': banners.first(),
    }
