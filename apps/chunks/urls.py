# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url

urlpatterns = patterns('chunks.views',
    url(r'^chunk/(?P<key>.+)\.(?P<lang>.+)\.html$', 'chunk', name='chunk'),
)
