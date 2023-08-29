# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.shortcuts import render, get_object_or_404
from libraries.models import Catalog, Library


def main_view(request):
    return render(request, 'libraries/main_view.html', {
        "catalogs": Catalog.objects.all(),
    })


def catalog_view(request, slug):
    return render(request, 'libraries/catalog_view.html', {
        "catalog": get_object_or_404(Catalog.objects.filter(slug=slug).select_related()),
    })

def library_view(request, catalog_slug, slug):
    return render(request, 'libraries/library_view.html', {
        "library": get_object_or_404(Library.objects.filter(slug=slug).filter(catalog__slug=catalog_slug)),
    })
