# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    'contact.views',
    url(r'^(?P<form_tag>[^/]+)/$', views.form, name='contact_form'),
    url(r'^(?P<form_tag>[^/]+)/thanks/$', views.thanks, name='contact_thanks'),
    url(r'^attachment/(?P<contact_id>\d+)/(?P<tag>[^/]+)/$', views.attachment, name='contact_attachment'),
    url(r'^results/(?P<contact_id>\d+)/(?P<digest>[0-9a-f]+)/', views.results, name='contact_results'),
)
