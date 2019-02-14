# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.main, name='wlsearch'),
    url(r'^hint/$', views.hint, name='search_hint'),
]
