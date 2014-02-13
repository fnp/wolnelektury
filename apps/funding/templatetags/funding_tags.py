# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from ..models import Offer
from ..utils import sanitize_payment_title

register = template.Library()


@register.inclusion_tag("funding/tags/funding.html", takes_context=True)
def funding(context, offer=None, link=False, closeable=False, show_title=True, show_title_calling=True, add_class=""):
    if offer is None and context.get('funding_no_show_current') is None:
        offer = Offer.current()
        is_current = True
    elif offer is not None:
        is_current = offer.is_current()

    if offer is None:
        return {}

    offer_sum = offer.sum()
    return {
        'offer': offer,
        'sum': offer_sum,
        'is_current': is_current,
        'is_win': offer_sum >= offer.target,
        'missing': offer.target - offer_sum,
        'percentage': 100 * offer_sum / offer.target,
        'link': link,
        'closeable': closeable,
        'show_title': show_title,
        'show_title_calling': show_title_calling,
        'add_class': add_class,
    }


@register.inclusion_tag("funding/tags/offer_status.html")
def offer_status(offer):
    return {
        'offer': offer,
    }

@register.inclusion_tag("funding/tags/offer_status_more.html")
def offer_status_more(offer):
    return {
        'offer': offer,
    }

register.filter(sanitize_payment_title)
