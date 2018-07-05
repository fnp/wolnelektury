# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from django.utils.functional import lazy
from django.utils.cache import add_never_cache_headers
from catalogue.models import Book
from ssify import ssi_variable
from ssify.utils import ssi_vary_on_cookie
from social.utils import likes, get_or_choose_cite

register = template.Library()


@ssi_variable(register, patch_response=[ssi_vary_on_cookie])
def likes_book(request, book_id):
    return likes(request.user, Book.objects.get(pk=book_id), request)


@ssi_variable(register, name='choose_cite', patch_response=[add_never_cache_headers])
def choose_cite_tag(request, book_id=None, tag_ids=None):
    cite = get_or_choose_cite(request, book_id, tag_ids)
    return cite.pk if cite is not None else None


@register.inclusion_tag('social/cite_promo.html')
def render_cite(cite):
    return {
        'cite': cite,
    }


@ssi_variable(register, patch_response=[ssi_vary_on_cookie])
def book_shelf_tags(request, book_id):
    if not request.user.is_authenticated():
        return ''
    book = Book.objects.get(pk=book_id)
    lks = likes(request.user, book, request)

    def get_value():
        if not lks:
            return ''
        tags = book.tags.filter(category='set', user=request.user).exclude(name='')
        if not tags:
            return ''
        ctx = {'tags': tags}
        return template.loader.render_to_string('social/shelf_tags.html', ctx)
    return lazy(get_value, unicode)()
