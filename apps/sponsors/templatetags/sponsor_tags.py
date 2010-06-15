# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from django.utils.safestring import mark_safe

from sponsors import models


register = template.Library()


def sponsor_page(name):
    try:
        page = models.SponsorPage.objects.get(name=name)
    except:
        return u''
    return mark_safe(page.html)

sponsor_page = register.simple_tag(sponsor_page)
