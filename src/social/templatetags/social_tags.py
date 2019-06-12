# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
from django import template
from django.utils.functional import lazy
from django.utils.cache import add_never_cache_headers
from catalogue.models import Book
from ssify import ssi_variable
from ssify.utils import ssi_vary_on_cookie
from social.utils import likes, get_or_choose_cite
from ..models import Carousel, Cite

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
    return lazy(get_value, str)()


@register.inclusion_tag('social/carousel.html', takes_context=True)
def carousel(context, slug):
    # TODO: cache
    try:
        carousel = Carousel.objects.get(slug=slug)
    except Carousel.DoesNotExist:
        # TODO: add sanity check for install.
        carousel = None
    banners = [
            item.get_banner()
            for item in carousel.carouselitem_set.all()
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


@register.inclusion_tag('social/embed_video.html')
def embed_video(url):
    m = re.match(r'https://www.youtube.com/watch\?v=([^&;]+)', url)
    return {
        'youtube_id': m.group(1) if m else None,
    }
