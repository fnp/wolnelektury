# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from django.views.decorators.cache import never_cache
from . import views


urlpatterns = [
    path('lektura/<slug:slug>/lubie/', views.like_book, name='social_like_book'),
    path('dodaj-tag/', views.AddSetView.as_view(), name='social_add_set_tag'),
    path('usun-tag/', views.RemoveSetView.as_view(), name='social_remove_set_tag'),
    path('moje-tagi/', views.my_tags, name='social_my_tags'),
    path('lektura/<slug:slug>/nie_lubie/', views.unlike_book, name='social_unlike_book'),
    path('lektura/<slug:slug>/polki/', never_cache(views.ObjectSetsFormView()), name='social_book_sets'),
    path('polka/', views.my_shelf, name='social_my_shelf'),
    path('ulubione/', views.my_liked),
]
