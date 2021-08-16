from django.template import Library


register = Library()


@register.filter
def first_part(txt, sep):
    return txt.split(sep, 1)[0]


@register.filter
def second_part(txt, sep):
    parts = txt.split(sep, 1)
    return parts[1] if len(parts) > 1 else ''

