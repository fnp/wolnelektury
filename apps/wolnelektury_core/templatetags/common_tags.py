# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
register = template.Library()


@register.filter
def build_absolute_uri(uri, request):
    return request.build_absolute_uri(uri)
