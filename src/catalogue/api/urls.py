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
]
