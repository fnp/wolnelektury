# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path
from stats.utils import piwik_track_view
from . import views


urlpatterns = [
    path('like/<slug:slug>/',
        piwik_track_view(views.LikeView2.as_view()),
        name='social_api_like'),
    path('likes/', views.LikesView.as_view()),
    path('my-likes/', views.MyLikesView.as_view()),

    path('lists/', views.ListsView.as_view()),
    path('lists/<slug:slug>/', views.ListView.as_view()),
    path('lists/<slug:slug>/<slug:book>/', views.ListItemView.as_view()),

    path('progress/', views.ProgressListView.as_view()),
    path('progress/<slug:slug>/', views.ProgressView.as_view()),
    path('progress/<slug:slug>/text/', views.TextProgressView.as_view()),
    path('progress/<slug:slug>/audio/', views.AudioProgressView.as_view()),

    path('sync/', views.SyncView.as_view()),
]


