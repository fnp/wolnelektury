# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls.defaults import *
from catalogue.feeds import RootFeed, ByCategoryFeed, ByTagFeed, UserFeed, UserSetFeed


urlpatterns = patterns('catalogue.views',
    url(r'^$', 'main_page', name='main_page'),
    url(r'^polki/(?P<shelf>[a-zA-Z0-9-]+)/formaty/$', 'shelf_book_formats', name='shelf_book_formats'),
    url(r'^polki/(?P<shelf>[a-zA-Z0-9-]+)/(?P<book>[a-zA-Z0-9-0-]+)/usun$', 'remove_from_shelf', name='remove_from_shelf'),
    url(r'^polki/$', 'user_shelves', name='user_shelves'),
    url(r'^polki/(?P<slug>[a-zA-Z0-9-]+)/usun/$', 'delete_shelf', name='delete_shelf'),
    url(r'^polki/(?P<slug>[a-zA-Z0-9-]+)\.zip$', 'download_shelf', name='download_shelf'),
    url(r'^lektury/', 'book_list', name='book_list'),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)/polki/', 'book_sets', name='book_shelves'),
    url(r'^polki/nowa/$', 'new_set', name='new_set'),
    url(r'^tags/$', 'tags_starting_with', name='hint'),
    url(r'^jtags/$', 'json_tags_starting_with', name='jhint'),
    url(r'^szukaj/$', 'search', name='search'),

    # tools
    url(r'^zegar', 'clock', name='clock'),

    # OPDS interface
    url(r'^opds/$', RootFeed(), name="opds_authors"),
    url(r'^opds/user/$', UserFeed(), name="opds_user"),
    url(r'^opds/set/(?P<slug>[a-zA-Z0-9-]+)/$', UserSetFeed(), name="opds_user_set"),
    url(r'^opds/(?P<category>[a-zA-Z0-9-]+)/$', ByCategoryFeed(), name="opds_by_category"),
    url(r'^opds/(?P<category>[a-zA-Z0-9-]+)/(?P<slug>[a-zA-Z0-9-]+)/$', ByTagFeed(), name="opds_by_tag"),

    # Public interface. Do not change this URLs.
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)\.html$', 'book_text', name='book_text'),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)/$', 'book_detail', name='book_detail'),
    url(r'^lektura/(?P<book_slug>[a-zA-Z0-9-]+)/motyw/(?P<theme_slug>[a-zA-Z0-9-]+)/$',
        'book_fragments', name='book_fragments'),
    url(r'^(?P<tags>[a-zA-Z0-9-/]*)/$', 'tagged_object_list', name='tagged_object_list'),
)

