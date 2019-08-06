# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import include, url
from stats.utils import piwik_track_view
from . import views


urlpatterns = [
    url(r'^like/(?P<slug>[a-z0-9-]+)/$',
        piwik_track_view(views.LikeView.as_view()),
        name='social_api_like'),
    url(r'^shelf/(?P<state>[a-z]+)/$',
        piwik_track_view(views.ShelfView.as_view()),
        name='social_api_shelf'),
]
