# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import catalogue.views
from stats.utils import piwik_track_view
from . import views


urlpatterns = [
    url(r'^oauth/request_token/$', views.OAuth1RequestTokenView.as_view()),
    url(r'^oauth/authorize/$', views.oauth_user_auth, name='oauth_user_auth'),
    url(r'^oauth/access_token/$', csrf_exempt(views.OAuth1AccessTokenView.as_view())),

    url(r'^$', TemplateView.as_view(template_name='api/main.html'), name='api'),

    # info boxes (used by mobile app)
    url(r'book/(?P<book_id>\d*?)/info\.html$', catalogue.views.book_info),
    url(r'tag/(?P<tag_id>\d*?)/info\.html$', catalogue.views.tag_info),

    # reading data
    url(r'^reading/(?P<slug>[a-z0-9-]+)/$',
        piwik_track_view(views.BookUserDataView.as_view()),
        name='api_reading'),
    url(r'^reading/(?P<slug>[a-z0-9-]+)/(?P<state>[a-z]+)/$',
        piwik_track_view(views.BookUserDataView.as_view()),
        name='api_reading'),
    url(r'^username/$',
        piwik_track_view(views.UserView.as_view()),
        name='api_username'),

    url(r'^blog$',
        piwik_track_view(views.BlogView.as_view())),

    url(r'^pictures/', include('picture.api.urls')),
    url(r'^', include('social.api.urls')),
    url(r'^', include('catalogue.api.urls')),
]
