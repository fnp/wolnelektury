# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Template, TemplateSyntaxError

from infopages.models import InfoPage


def infopage(request, slug):
    page = get_object_or_404(InfoPage, slug=slug)
    rc = RequestContext(request)
    try:
        left_column = Template(page.left_column).render(rc)
    except TemplateSyntaxError:
        left_column = ''

    try:
        right_column = Template(page.right_column).render(rc)
    except TemplateSyntaxError:
        left_column = ''

    return render_to_response('infopages/infopage.html', locals(),
                context_instance=RequestContext(request))
