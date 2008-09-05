# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('catalogue.views',
    url(r'^$', 'main_page', name='main_page'),
    url(r'^lektury/', 'book_list'),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)/polki/', 'book_sets'),
    url(r'^polki/nowa/$', 'new_set'),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)/$', 'book_detail'),
    url(r'^tags/$', 'tags_starting_with', name='hint'),
    url(r'^szukaj/$', 'search', name='search'),
    url(r'^(?P<tags>[a-zA-Z-/]+)/$', 'tagged_object_list', name='tagged_object_list'),
)

