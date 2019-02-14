# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.main_view, name='libraries_main_view'),
    url(r'^(?P<slug>[a-zA-Z0-9_-]+)$', views.catalog_view, name='libraries_catalog_view'),
    url(r'^(?P<catalog_slug>[a-zA-Z0-9_-]+)/(?P<slug>[a-zA-Z0-9_-]+)$', views.library_view, name='libraries_library_view'),
]
