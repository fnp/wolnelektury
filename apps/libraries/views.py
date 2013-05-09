from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Template, TemplateSyntaxError

from libraries.models import Catalog


def main_view(request, slug):
    context = RequestContext(request)
    context['catalog'] = get_object_or_404(Catalog.objects.filter(slug = slug).select_related())
    return render_to_response('libraries/main_view.html', context_instance = context)