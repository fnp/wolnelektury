# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from libraries.models import Catalog, Library


def main_view(request):
    context = RequestContext(request)
    context['catalogs'] = Catalog.objects.all()
    return render_to_response('libraries/main_view.html', context_instance=context)

def catalog_view(request, slug):
    context = RequestContext(request)
    context['catalog'] = get_object_or_404(Catalog.objects.filter(slug=slug).select_related())
    return render_to_response('libraries/catalog_view.html', context_instance=context)
    
def library_view(request, catalog_slug, slug):
    context = RequestContext(request)
    context['library'] = get_object_or_404(Library.objects.filter(slug=slug).filter(catalog__slug=catalog_slug))
    return render_to_response('libraries/library_view.html', context_instance=context)
