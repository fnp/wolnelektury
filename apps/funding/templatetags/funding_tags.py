# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from ssify import ssi_variable
from ssify.utils import ssi_cache_control
from ..models import Offer
from ..utils import sanitize_payment_title

register = template.Library()


@ssi_variable(register, patch_response=[ssi_cache_control(must_revalidate=True, max_age=0)])
def current_offer(request):
    offer = Offer.current()
    return offer.pk if offer is not None else None


register.filter(sanitize_payment_title)
