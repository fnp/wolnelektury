# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url, include

from .models import Offer
from .views import (WLFundView, OfferDetailView, OfferListView,
                FundingView)


urlpatterns = patterns('',
    url(r'^$', OfferDetailView.as_view(), name='funding_current'),
    url(r'^lektura/$', OfferListView.as_view(), name='funding'),
    url(r'^lektura/(?P<slug>[^/]+)/$', OfferDetailView.as_view(), name='funding_offer'),
    url(r'^wplata/(?P<pk>\d+)/$', FundingView.as_view(), name='funding_funding'),
    url(r'^fundusz/$', WLFundView.as_view(), name='funding_wlfund'),
    url(r'^getpaid/', include('getpaid.urls')),
)
