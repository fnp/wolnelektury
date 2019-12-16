# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path('', views.main_view, name='libraries_main_view'),
    path('<slug:slug>', views.catalog_view, name='libraries_catalog_view'),
    path('<slug:catalog_slug>/<slug:slug>', views.library_view, name='libraries_library_view'),
]
