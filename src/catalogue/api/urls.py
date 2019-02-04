# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import include, url
from . import views


tags_re = r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){0,6})'
paginate_re = r'(?:after/(?P<after>[a-z0-9-]+)/)?(?:count/(?P<count>[0-9]+)/)?$'


urlpatterns = [
    # books by collections
    url(r'^collections/$', views.CollectionList.as_view(), name="api_collections"),
    url(r'^collections/(?P<slug>[^/]+)/$',
        views.CollectionDetail.as_view(), name="collection-detail"),

    url(tags_re + r'books/' + paginate_re,
        views.BookList.as_view(), name='catalogue_api_book_list'),
    url(tags_re + r'parent_books/' + paginate_re,
        views.BookList.as_view(), {"top_level": True}, name='catalogue_api_parent_book_list'),
    url(tags_re + r'audiobooks/' + paginate_re,
        views.BookList.as_view(), {"audiobooks": True}, name='catalogue_api_audiobook_list'),
    url(tags_re + r'daisy/' + paginate_re,
        views.BookList.as_view(), {"daisy": True}, name='catalogue_api_daisy_list'),
    url(r'^recommended/' + paginate_re,
        views.BookList.as_view(),
        {"recommended": True}, name='catalogue_api_recommended_list'),
    url(r'^newest/$',
        views.BookList.as_view(),
        {"newest": True, "top_level": True, "count": 20}, name='catalogue_api_newest_list'),

    url(r'^books/(?P<slug>[^/]+)/$', views.BookDetail.as_view(), name='catalogue_api_book'),

    url(r'^epub/(?P<slug>[a-z0-9-]+)/$', views.EpubView.as_view(), name='catalogue_api_epub'),

    url(r'^preview/$', views.Preview.as_view(), name='catalogue_api_preview'),

    url(r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){1,6})fragments/$', views.FragmentList.as_view()),
    url(r'^books/(?P<book>[a-z0-9-]+)/fragments/(?P<anchor>[a-z0-9-]+)/$',
        views.FragmentView.as_view(), name="catalogue_api_fragment"),

    url(r'^(?P<category>[a-z]+)s/$', views.TagCategoryView.as_view(), name='catalogue_api_tag_list'),
    url(r'^(?P<category>[a-z]+)s/(?P<slug>[a-z0-9-]+)/$', views.TagView.as_view(), name="catalogue_api_tag"),
]
