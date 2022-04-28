"""Piwik template tag."""

from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


register = template.Library()


@register.inclusion_tag('piwik/tracking_code.html', takes_context=True)
def tracking_code(context):
    try:
        id = settings.PIWIK_SITE_ID
    except AttributeError:
        raise ImproperlyConfigured('PIWIK_SITE_ID does not exist.')
    try:
        url = settings.PIWIK_URL
    except AttributeError:
        raise ImproperlyConfigured('PIWIK_URL does not exist.')
    return {'id': id, 'url': url, 'request': context.get('request')}
