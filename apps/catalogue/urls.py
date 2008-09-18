# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('catalogue.views',
    url(r'^$', 'main_page', name='main_page'),
    url(r'^polki/$', 'user_shelves', name='user_shelves'),
    url(r'^polki/(?P<slug>[a-zA-Z0-9-]+)/usun/$', 'delete_shelf', name='delete_shelf'),
    url(r'^polki/(?P<slug>[a-zA-Z0-9-]+)\.zip$', 'download_shelf', name='download_shelf'),
    url(r'^lektury/', 'book_list', name='book_list'),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)/polki/', 'book_sets', name='book_shelves'),
    url(r'^polki/nowa/$', 'new_set', name='new_set'),
    url(r'^tags/$', 'tags_starting_with', name='hint'),
    url(r'^szukaj/$', 'search', name='search'),
    
    # Public interface. Do not change this URLs.
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)\.html$', 'book_text', name='book_text'),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)/$', 'book_detail', name='book_detail'),
    url(r'^(?P<tags>[a-zA-Z0-9-/]+)/$', 'tagged_object_list', name='tagged_object_list'),
)

