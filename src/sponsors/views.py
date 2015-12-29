# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.http import HttpResponse
from ssify import ssi_included
from .models import SponsorPage


@ssi_included(use_lang=False)
def page(request, name):
    try:
        page = SponsorPage.objects.get(name=name)
    except SponsorPage.DoesNotExist:
        return HttpResponse(u'')
    return HttpResponse(page.html)
