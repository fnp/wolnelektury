# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from infopages.models import InfoPage

register = template.Library()


@register.inclusion_tag('infopages/on_main.html')
def infopages_on_main():
    objects = InfoPage.objects.exclude(main_page=None)
    return {"objects": objects}
