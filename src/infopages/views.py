# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext, Template, TemplateSyntaxError

from infopages.models import InfoPage


def infopage(request, slug):
    if request.user.is_staff:
        page = get_object_or_404(InfoPage, slug=slug)
    else:
        page = get_object_or_404(InfoPage, slug=slug, published=True)

    rc = RequestContext(request)
    try:
        left_column = Template(page.left_column).render(rc)
    except TemplateSyntaxError:
        left_column = ''

    try:
        right_column = Template(page.right_column).render(rc)
    except TemplateSyntaxError:
        right_column = ''

    return render(
        request,
        'infopages/infopage.html',
        {
            'page': page,
            'left_column': left_column,
            'right_column': right_column,
            'active_menu_item': f'info:{slug}',
        }
    )
