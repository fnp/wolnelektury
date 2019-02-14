# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.stats_page, name='reporting_stats'),
    url(r'^katalog.pdf$', views.catalogue_pdf, name='reporting_catalogue_pdf'),
    url(r'^katalog.csv$', views.catalogue_csv, name='reporting_catalogue_csv'),
]
