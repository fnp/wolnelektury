# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView, FormView

from .models import Offer
from .views import WLFundView


urlpatterns = patterns('',
    url(r'^$', ListView.as_view(queryset=Offer.public()), name='funding'),
    url(r'lektura/^(?P<slug>[^/]+)/$', DetailView.as_view(queryset=Offer.public()), name='funding_offer'),
    url(r'fundusz/$', WLFundView.as_view(), name='funding_wlfund'),
)
