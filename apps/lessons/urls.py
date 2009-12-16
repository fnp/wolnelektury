# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from catalogue import forms
from lessons import models


urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.list_detail.object_list', {
        'queryset': models.Document.objects.all(),
        'template_name': 'lessons/document_list.html',
        'extra_context': {
            'form': forms.SearchForm(),
        },
    }, name='lessons_document_list'),
    
    url(r'^(?P<slug>[a-zA-Z0-9_-]+)/$', 'lessons.views.document_detail', name='lessons_document_detail'),
)

