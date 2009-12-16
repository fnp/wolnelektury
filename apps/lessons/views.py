from django.views.generic.list_detail import object_detail
from catalogue import forms
from lessons import models


def document_detail(request, slug):
    template_name = 'lessons/document_detail.html'
    if request.is_ajax():
        template_name = 'lessons/ajax_document_detail.html'
    
    return object_detail(request,
        slug=slug,
        slug_field='slug',
        queryset=models.Document.objects.all(),
        template_name=template_name,
        extra_context={
            'form': forms.SearchForm(),
        })
