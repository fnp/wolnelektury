from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Template, TemplateSyntaxError

from libraries.models import Library


def main_view(request):
    context = RequestContext(request)
    context['libraries'] = Library.objects.all()

    return render_to_response('libraries/main_view.html', context_instance = context)