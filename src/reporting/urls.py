# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path('', views.stats_page, name='reporting_stats'),
    path('katalog.pdf', views.catalogue_pdf, name='reporting_catalogue_pdf'),
    path('katalog.csv', views.catalogue_csv, name='reporting_catalogue_csv'),
]
