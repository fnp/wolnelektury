# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path
from opds.views import RootFeed, ByCategoryFeed, ByTagFeed, UserFeed, UserSetFeed, SearchFeed


urlpatterns = [
    path('', RootFeed(), name="opds_authors"),
    path('search/', SearchFeed(), name="opds_search"),
    path('user/', UserFeed(), name="opds_user"),
    path('set/<slug>/', UserSetFeed(), name="opds_user_set"),
    path('<category>/', ByCategoryFeed(), name="opds_by_category"),
    path('<category>/<slug>/', ByTagFeed(), name="opds_by_tag"),
]
