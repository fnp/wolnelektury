from django.shortcuts import render
from . import models


def map(request):
    return render(request, 'references/map.html', {
        'entities': models.Entity.objects.exclude(lat=None).exclude(lon=None),
    })
                  
