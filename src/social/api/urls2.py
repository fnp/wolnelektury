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
]


