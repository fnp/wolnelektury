from django.template import Library
from ..models import Menu


register = Library()


@register.inclusion_tag('chunks/menu.html')
def menu(identifier):
    menu, created = Menu.objects.get_or_create(identifier=identifier)
        
    return {
        'menu': menu,
    }
