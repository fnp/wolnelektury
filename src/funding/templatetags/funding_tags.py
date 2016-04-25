# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from ssify import ssi_variable
from ssify.utils import ssi_cache_control

from ..models import Offer
from ..utils import sanitize_payment_title
from ..views import offer_bar

register = template.Library()


@ssi_variable(register, patch_response=[ssi_cache_control(must_revalidate=True, max_age=0)])
def current_offer(request=None):
    offer = Offer.current()
    return offer.pk if offer is not None else None


@register.inclusion_tag('funding/includes/funding.html')
def funding_top_bar():
    return offer_bar(Offer.current(), link=True, closeable=True, add_class="funding-top-header")


register.filter(sanitize_payment_title)
