from django import template
from django.template import Node, Variable, Template, Context
from catalogue.utils import split_tags

register = template.Library()

@register.inclusion_tag('picture/picture_short.html', takes_context=True)
def picture_short(context, picture):
    return {
        'picture': picture,
        'main_link': picture.get_absolute_url(),
        # 'related': picture.related_info(),
        'request': context.get('request'),
        'tags': split_tags(picture.tags),
        }
                            
@register.inclusion_tag('picture/picture_wide.html', takes_context=True)
def picture_wide(context, picture):
    return {
        'picture': picture,
        'main_link': picture.get_absolute_url(),
        # 'related': picture.related_info(),
        'request': context.get('request'),
        'tags': split_tags(picture.tags),
        }

