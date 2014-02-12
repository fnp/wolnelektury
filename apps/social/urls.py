# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url
from social.views import ObjectSetsFormView

urlpatterns = patterns('social.views',
    url(r'^lektura/(?P<slug>[a-z0-9-]+)/lubie/$', 'like_book', name='social_like_book'),
    url(r'^lektura/(?P<slug>[a-z0-9-]+)/nie_lubie/$', 'unlike_book', name='social_unlike_book'),
    url(r'^lektura/(?P<slug>[a-z0-9-]+)/polki/$', ObjectSetsFormView(), name='social_book_sets'),
    url(r'^polka/$', 'my_shelf', name='social_my_shelf'),

    #~ url(r'^polki/(?P<shelf>[a-zA-Z0-9-]+)/formaty/$', 'shelf_book_formats', name='shelf_book_formats'),
    #~ url(r'^polki/(?P<shelf>[a-zA-Z0-9-]+)/(?P<slug>%s)/usun$' % SLUG, 'remove_from_shelf', name='remove_from_shelf'),
    #~ url(r'^polki/$', 'user_shelves', name='user_shelves'),
    #~ url(r'^polki/(?P<slug>[a-zA-Z0-9-]+)/usun/$', 'delete_shelf', name='delete_shelf'),
    #~ url(r'^polki/(?P<slug>[a-zA-Z0-9-]+)\.zip$', 'download_shelf', name='download_shelf'),
    #~ url(r'^polki/nowa/$', 'new_set', name='new_set'),
) 
