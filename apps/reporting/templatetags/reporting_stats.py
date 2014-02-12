# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import feedparser
from functools import wraps
import datetime

from django import template

from catalogue.models import Book, BookMedia


register = template.Library()

class StatsNode(template.Node):
    def __init__(self, value, varname=None):
        self.value = value
        self.varname = varname

    def render(self, context):
        if self.varname:
            context[self.varname] = self.value
            return ''
        else:
            return self.value


def register_counter(f):
    """Turns a simple counting function into a registered counter tag.

    You can run a counter tag as a simple {% tag_name %} tag, or
    as {% tag_name var_name %} to store the result in a variable.

    """
    @wraps(f)
    def wrapped(parser, token):
        try:
            tag_name, args = token.contents.split(None, 1)
        except ValueError:
            args = None
        return StatsNode(f(), args)

    return register.tag(wrapped)


@register_counter
def count_books_all():
    return Book.objects.all().count()

@register_counter
def count_books():
    return Book.objects.filter(children=None).count()

@register_counter
def count_books_parent():
    return Book.objects.exclude(children=None).count()

@register_counter
def count_books_root():
    return Book.objects.filter(parent=None).count()
