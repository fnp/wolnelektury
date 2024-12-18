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
]
