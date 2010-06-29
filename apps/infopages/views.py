# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.shortcuts import render_to_response
from django.template import RequestContext

from catalogue.forms import SearchForm
from infopages.models import InfoPage

def infopage(request, slug):
    form = SearchForm()
    object = InfoPage.objects.get(slug=slug)

    return render_to_response('info/base.html', locals(),
                context_instance=RequestContext(request))