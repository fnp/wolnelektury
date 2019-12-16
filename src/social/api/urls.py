# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from stats.utils import piwik_track_view
from . import views


urlpatterns = [
    path('like/<slug:slug>/',
        piwik_track_view(views.LikeView.as_view()),
        name='social_api_like'),
    path('shelf/<slug:state>/',
        piwik_track_view(views.ShelfView.as_view()),
        name='social_api_shelf'),
]
