# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from catalogue.models import Book
from social.models import Cite
from social.utils import likes, cites_for_tags

register = template.Library()

register.filter('likes', likes)


@register.inclusion_tag('social/cite_promo.html')
def cite_promo(ctx=None, fallback=False):
    """Choose"""
    if ctx is None:
        cites = Cite.objects.all()
    elif isinstance(ctx, Book):
        cites = ctx.cite_set.all()
        if not cites.exists():
            cites = cites_for_tags([ctx.book_tag()])
    else:
        cites = cites_for_tags(ctx)

    return {
        'cite': cites.order_by('?')[0] if cites.exists() else None,
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
