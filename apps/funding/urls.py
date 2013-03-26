# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url
from django.views.generic import ListView, FormView, TemplateView

from .models import Offer
from .views import WLFundView, OfferDetailView, ThanksView


urlpatterns = patterns('',
    url(r'^$', ListView.as_view(queryset=Offer.public()), name='funding'),
    url(r'^lektura/(?P<slug>[^/]+)/$', OfferDetailView.as_view(), name='funding_offer'),
    url(r'^dziekujemy/$', ThanksView.as_view(), name='funding_thanks'),
    url(r'^fundusz/$', WLFundView.as_view(), name='funding_wlfund'),
)
