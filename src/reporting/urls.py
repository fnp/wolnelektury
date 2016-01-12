# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url


urlpatterns = patterns(
    'reporting.views',
    url(r'^$', 'stats_page', name='reporting_stats'),
    url(r'^katalog.pdf$', 'catalogue_pdf', name='reporting_catalogue_pdf'),
    url(r'^katalog.csv$', 'catalogue_csv', name='reporting_catalogue_csv'),
)
