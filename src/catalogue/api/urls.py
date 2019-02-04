# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import include, url
from . import views


urlpatterns = [
    # books by collections
    url(r'^collections/$', views.CollectionList.as_view(), name="api_collections"),
    url(r'^collections/(?P<slug>[^/]+)/$',
        views.CollectionDetail.as_view(), name="collection-detail"),

    url(r'^books/(?P<slug>[^/]+)/$', views.BookDetail.as_view(), name='catalogue_api_book'),

    url(r'^epub/(?P<slug>[a-z0-9-]+)/$', views.EpubView.as_view(), name='catalogue_api_epub'),

    url(r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){1,6})fragments/$', views.FragmentList.as_view()),
    url(r'^books/(?P<book>[a-z0-9-]+)/fragments/(?P<anchor>[a-z0-9-]+)/$',
        views.FragmentView.as_view(), name="catalogue_api_fragment"),

    url(r'^(?P<category>[a-z]+)s/$', views.TagCategoryView.as_view(), name='catalogue_api_tag_list'),
    url(r'^(?P<category>[a-z]+)s/(?P<slug>[a-z0-9-]+)/$', views.TagView.as_view(), name="catalogue_api_tag"),
]
