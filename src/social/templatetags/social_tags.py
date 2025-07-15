# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import re
from django import template
from django.utils.cache import add_never_cache_headers
from catalogue.models import Book, Fragment
from social.utils import likes, get_or_choose_cite, choose_cite as cs
from ..models import Carousel, Cite

register = template.Library()


@register.simple_tag(takes_context=True)
def likes_book(context, book):
    request = context['request']
    return likes(request.user, book, request)


@register.simple_tag(takes_context=True)
def choose_cite(context, book_id=None, tag_ids=None):
    request = context['request']
    return get_or_choose_cite(request, book_id, tag_ids)


@register.simple_tag
def choose_cites(number, book=None, author=None):
    if book is not None:
        return book.choose_fragments(number) # todo: cites?
    elif author is not None:
        return Fragment.tagged.with_all([author]).order_by('?')[:number]


@register.inclusion_tag('social/carousel.html', takes_context=True)
def carousel(context, placement):
    banners = Carousel.get(placement).carouselitem_set.all()#first().get_banner()
    return {
        'banners': [b.get_banner() for b in banners],
    }


@register.inclusion_tag('social/embed_video.html')
def embed_video(url):
    m = re.match(r'https://www.youtube.com/watch\?v=([^&;]+)', url)
    return {
        'youtube_id': m.group(1) if m else None,
    }
