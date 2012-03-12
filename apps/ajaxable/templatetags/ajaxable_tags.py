from django import template
from ajaxable.utils import placeholdized
register = template.Library()


@register.filter
def placeholdize(form):
    return placeholdized(form)


@register.filter
def placeholdized_ul(form):
    return placeholdized(form).as_ul()
