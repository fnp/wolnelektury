# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import catalogue.views
from stats.utils import piwik_track_view
from . import views


urlpatterns = [
    path('oauth/request_token/', csrf_exempt(views.OAuth1RequestTokenView.as_view())),
    path('oauth/authorize/', views.oauth_user_auth, name='oauth_user_auth'),
    path('oauth/access_token/', csrf_exempt(views.OAuth1AccessTokenView.as_view())),

    path('', TemplateView.as_view(template_name='api/main.html'), name='api'),

    # info boxes (used by mobile app)
    path('book/<int:book_id>/info.html', catalogue.views.book_info),
    path('tag/<int:tag_id>/info.html', catalogue.views.tag_info),

    # reading data
    path('reading/<slug:slug>/',
         piwik_track_view(views.BookUserDataView.as_view()),
         name='api_reading'),
    path('reading/<slug:slug>/<slug:state>/',
         piwik_track_view(views.BookUserDataView.as_view()),
         name='api_reading'),
    path('username/',
         piwik_track_view(views.UserView.as_view()),
         name='api_username'),

    path('blog',
         piwik_track_view(views.BlogView.as_view())),

    path('pictures/', include('picture.api.urls')),
    path('', include('social.api.urls')),
    path('', include('catalogue.api.urls')),
]
