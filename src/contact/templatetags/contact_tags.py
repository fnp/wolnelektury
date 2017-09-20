# -*- coding: utf-8 -*-
from django.template import Library
from contact.models import Contact

register = Library()


@register.filter
def pretty_print(value):
    return Contact.pretty_print(value)
