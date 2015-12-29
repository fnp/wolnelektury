# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from ajaxable.utils import placeholdized
register = template.Library()


@register.filter
def placeholdize(form):
    return placeholdized(form)


@register.filter
def placeholdized_ul(form):
    return placeholdized(form).as_ul()
