# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url
from suggest import views

urlpatterns = patterns(
    '',
    url(r'^$', views.SuggestionFormView(), name='suggest'),
    url(r'^plan/$', views.PublishingSuggestionFormView(), name='suggest_publishing'),
)
