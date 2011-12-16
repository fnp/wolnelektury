from django.template import RequestContext
from django.shortcuts import render_to_response
from catalogue.models import Book


def main_page(request):
    last_published = Book.objects.exclude(html_file='').order_by('-created_at')[:4]

    return render_to_response("main_page.html", locals(),
        context_instance=RequestContext(request))