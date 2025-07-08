from django.template import Library


register = Library()

@register.simple_tag(takes_context=True)
def title(context, t=None):
    context.dicts[0]['title'] = t
    return ''

@register.simple_tag(takes_context=True)
def set_global(context, variable, value=None):
    context.dicts[0][variable] = value
    return ''
