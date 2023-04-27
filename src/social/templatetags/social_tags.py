# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
from django import template
from django.utils.functional import lazy
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


@register.simple_tag(takes_context=True)
def book_shelf_tags(context, book_id):
    request = context['request']
    if not request.user.is_authenticated:
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
    return lazy(get_value, str)()


@register.inclusion_tag('social/carousel.html', takes_context=True)
def carousel(context, placement):
    carousel = Carousel.get(placement)
    banners = [
            item.get_banner()
            for item in carousel.carouselitem_set.all().select_related('banner')
            ]

    request = context['request']
    if 'banner' in request.GET:
        try:
            banner_id = int(request.GET['banner'])
        except (TypeError, ValueError):
            pass
        else:
            try:
                index = [b.pk for b in banners].index(banner_id)
            except ValueError:
                if request.user.is_staff:
                    # Staff is allowed to preview any banner.
                    try:
                        banners.insert(0, Cite.objects.get(pk=banner_id))
                    except Cite.DoesNotExist:
                        pass
            else:
                # Put selected banner to front.
                banners = [banners[index]] + banners[:index] + banners[index+1:]

    return {
        'carousel': carousel,
        'banners': banners,
    }


@register.inclusion_tag('social/carousel_2022.html', takes_context=True)
def carousel_2022(context, placement):
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
