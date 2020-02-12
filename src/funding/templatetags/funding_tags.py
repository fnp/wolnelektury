# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from django.template.loader import render_to_string
from django.core.paginator import Paginator, InvalidPage

from ..models import Offer
from ..utils import sanitize_payment_title


register = template.Library()


@register.simple_tag
def funding_top_bar():
    offer = Offer.current()
    return offer.top_bar() if offer is not None else ''


register.filter(sanitize_payment_title)


@register.simple_tag(takes_context=True)
def fundings(context, offer):
    fundings = offer.funding_payed()
    page = context['request'].GET.get('page', 1)
    paginator = Paginator(fundings, 10, 2)
    try:
        page_obj = paginator.page(int(page))
    except InvalidPage:
        return ''
    else:
        return render_to_string("funding/includes/fundings.html", {
            "paginator": paginator,
            "page_obj": page_obj,
            "fundings": page_obj.object_list,
        })
