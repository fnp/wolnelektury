from django import template
from ..helpers import get_active_schedule


register = template.Library()


@register.filter
def active_schedule(user):
    return get_active_schedule(user)
