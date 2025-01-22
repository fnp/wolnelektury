# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path, re_path
from stats.utils import piwik_track_view
from . import views


urlpatterns = [
    path('books/',
         piwik_track_view(views.BookList2.as_view()),
         name='catalogue_api_book_list'
         ),
    path('books/<slug:slug>/',
         piwik_track_view(views.BookDetail2.as_view()),
         name='catalogue_api_book'
         ),

    path('authors/',
         piwik_track_view(views.AuthorList.as_view()),
         name="catalogue_api_author_list"),
    path('authors/<slug:slug>/',
         piwik_track_view(views.AuthorView.as_view()),
         name='catalogue_api_author'),
    path('epochs/',
         piwik_track_view(views.EpochList.as_view()),
         name="catalogue_api_epoch_list"),
    path('epochs/<slug:slug>/',
         piwik_track_view(views.EpochView.as_view()),
         name='catalogue_api_epoch'),
    path('kinds/',
         piwik_track_view(views.KindList.as_view()),
         name="catalogue_api_kind_list"),
    path('kinds/<slug:slug>/',
         piwik_track_view(views.KindView.as_view()),
         name='catalogue_api_kind'),
    path('genres/',
         piwik_track_view(views.GenreList.as_view()),
         name="catalogue_api_genre_list"),
    path('genres/<slug:slug>/',
         piwik_track_view(views.GenreView.as_view()),
         name='catalogue_api_genre'),
]
