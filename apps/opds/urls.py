# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls.defaults import *
from opds.views import RootFeed, ByCategoryFeed, ByTagFeed, UserFeed, UserSetFeed, SearchFeed


urlpatterns = patterns('opds.views',
    url(r'^$', RootFeed(), name="opds_authors"),
    url(r'^search/$', SearchFeed(), name="opds_search"),
    url(r'^user/$', UserFeed(), name="opds_user"),
    url(r'^set/(?P<slug>[a-zA-Z0-9-]+)/$', UserSetFeed(), name="opds_user_set"),
    url(r'^(?P<category>[a-zA-Z0-9-]+)/$', ByCategoryFeed(), name="opds_by_category"),
    url(r'^(?P<category>[a-zA-Z0-9-]+)/(?P<slug>[a-zA-Z0-9-]+)/$', ByTagFeed(), name="opds_by_tag"),
)
