# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from random import randint
from django.db.models import Q
from django import template
from catalogue.models import Book
from social.models import Cite
from social.utils import likes, cites_for_tags

register = template.Library()

register.filter('likes', likes)


@register.assignment_tag(takes_context=True)
def choose_cite(context, ctx=None):
    """Choose a cite for main page, for book or for set of tags."""
    try:
        request = context['request']
        assert request.user.is_staff
        assert 'choose_cite' in request.GET
        cite = Cite.objects.get(pk=request.GET['choose_cite'])
    except (AssertionError, Cite.DoesNotExist):
        if ctx is None:
            cites = Cite.objects.all()
        elif isinstance(ctx, Book):
            cites = Cite.objects.filter(Q(book=ctx) | Q(book__ancestor=ctx))
        else:
            cites = cites_for_tags(ctx)
        stickies = cites.filter(sticky=True)
        count = stickies.count()
        if count:
            cite = stickies[randint(0, count - 1)]
        else:
            count = cites.count()
            if count:
                cite = cites[randint(0, count - 1)]
            else:
                cite = None
    return cite


@register.inclusion_tag('social/cite_promo.html')
def render_cite(cite):
    return {
        'cite': cite,
    }


@register.inclusion_tag('social/cite_promo.html', takes_context=True)
def cite_promo(context, ctx=None, fallback=False):
    return {
        'cite': choose_cite(context, ctx),
        'fallback': fallback,
        'ctx': ctx,
    }


@register.inclusion_tag('social/shelf_tags.html', takes_context=True)
def shelf_tags(context, book):
    user = context['request'].user
    if not user.is_authenticated():
        tags = []
    else:
        tags = book.tags.filter(category='set', user=user).exclude(name='')
    return {'tags': tags}
