from django.views.decorators.cache import never_cache
from django.shortcuts import render, get_object_or_404
from . import models


def map(request):
    return render(request, 'references/map.html', {
        'entities': models.Entity.objects.exclude(lat=None).exclude(lon=None),
        'funding_no_show_current': True,
    })

@never_cache
def popup(request, pk):
    e = get_object_or_404(models.Entity, pk=pk)
    return render(request, 'references/popup.html', {
        'entity': e,
    })
    
