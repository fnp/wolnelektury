# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from django.views.decorators.cache import never_cache
from . import views


urlpatterns = [
    url(r'^lektura/(?P<slug>[a-z0-9-]+)/lubie/$', views.like_book, name='social_like_book'),
    url(r'^lektura/(?P<slug>[a-z0-9-]+)/nie_lubie/$', views.unlike_book, name='social_unlike_book'),
    url(r'^lektura/(?P<slug>[a-z0-9-]+)/polki/$', never_cache(views.ObjectSetsFormView()), name='social_book_sets'),
    url(r'^polka/$', views.my_shelf, name='social_my_shelf'),

    # Includes
    url(r'^cite/(?P<pk>\d+)\.(?P<lang>.+)\.html$', views.cite, name='social_cite'),
    url(r'^cite_main/(?P<pk>\d+)\.(?P<lang>.+)\.html$', views.cite, {'main': True}, name='social_cite_main'),
    url(r'^cite_info/(?P<pk>\d+).html$', views.cite_info, name='social_cite_info'),
]
