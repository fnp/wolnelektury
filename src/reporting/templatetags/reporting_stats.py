# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django import template
from catalogue.models import Book


register = template.Library()


@register.simple_tag
def count_books_all():
    return Book.objects.all().count()


@register.simple_tag
def count_books():
    print('count', Book.objects.filter(children=None).count())
    return Book.objects.filter(children=None).count()


@register.simple_tag
def count_books_parent():
    return Book.objects.exclude(children=None).count()


@register.simple_tag
def count_books_root():
    return Book.objects.filter(parent=None).count()
