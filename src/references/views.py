from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from catalogue.models import Book
from catalogue.views import analyse_tags
from . import models


def pin_map(request):
    return render(request, 'references/map.html', {
        'title': 'Mapa Wolnych Lektur',
        'entities': models.Entity.objects.exclude(lat=None).exclude(lon=None),
        'funding_no_show_current': True,
    })

def pin_map_tagged(request, tags):
    try:
        tags = analyse_tags(request, tags)
    except:
        raise #Http404()

    books = Book.tagged.with_all(tags)

    return render(request, 'references/map.html', {
        'entities': models.Entity.objects.exclude(lat=None).exclude(lon=None).filter(reference__book__in=books).distinct(),
        'funding_no_show_current': True,
    })


def popup(request, pk):
    e = get_object_or_404(models.Entity, pk=pk)
    return render(request, 'references/popup.html', {
        'entity': e,
    })
    
