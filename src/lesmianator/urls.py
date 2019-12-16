# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path('', views.main_page, name='lesmianator'),
    path('wiersz/', views.new_poem, name='new_poem'),
    path('lektura/<slug:slug>/', views.poem_from_book, name='poem_from_book'),
    path('polka/<shelf>/', views.poem_from_set, name='poem_from_set'),
    path('wiersz/<poem>/', views.get_poem, name='get_poem'),
]
