# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path
from . import views

urlpatterns = (
    path('dodaj/', views.add_isbn_wl, name='add_isbn_wl'),
    path('potwierdzenie/', views.confirm_isbn_wl, name='confirm_isbn_wl'),
    path('save-wl-onix/', views.save_wl_onix, name='save_wl_onix'),
    path('tagi-isbn/<slug:slug>/', views.wl_dc_tags, name='wl_dc_tags'),

    path('dodaj-fnp/', views.add_isbn_fnp, name='add_isbn_fnp'),
    path('przypisane/<slug:slug>/', views.assigned_isbn, name='assigned_isbn'),
)
