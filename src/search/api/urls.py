# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path('search/hint/', views.HintView.as_view()),
    path('search/', views.SearchView.as_view()),
    path('search/books/', views.BookSearchView.as_view()),
    path('search/text/', views.TextSearchView.as_view()),
]
