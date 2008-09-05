# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('catalogue.views',
    url(r'^$', 'main_page', name='main_page'),
    url(r'^polki/$', 'user_shelves', name='user_shelves'),
    url(r'^polki/(?P<slug>[a-zA-Z0-9-]+)/usun/$', 'delete_shelf', name='delete_shelf'),
    url(r'^lektury/', 'book_list', name='book_list'),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)/polki/', 'book_sets', name='book_shelves'),
    url(r'^fragment/(?P<id>[0-9]+)/polki/', 'fragment_sets', name='fragment_shelves'),
    url(r'^polki/nowa/$', 'new_set', name='new_set'),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)/$', 'book_detail', name='book_detail'),
    url(r'^tags/$', 'tags_starting_with', name='hint'),
    url(r'^szukaj/$', 'search', name='search'),
    url(r'^(?P<tags>[a-zA-Z-/]+)/$', 'tagged_object_list', name='tagged_object_list'),
)

