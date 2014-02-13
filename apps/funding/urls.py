# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url, include

from .views import (WLFundView, OfferDetailView, OfferListView,
                ThanksView, NoThanksView, CurrentView, DisableNotifications)


urlpatterns = patterns('',

    url(r'^$', CurrentView.as_view(), name='funding_current'),
    url(r'^teraz/$', CurrentView.as_view()),
    url(r'^teraz/(?P<slug>[^/]+)/$', CurrentView.as_view(), name='funding_current'),
    url(r'^lektura/$', OfferListView.as_view(), name='funding'),
    url(r'^lektura/(?P<slug>[^/]+)/$', OfferDetailView.as_view(), name='funding_offer'),
    url(r'^pozostale/$', WLFundView.as_view(), name='funding_wlfund'),

    url(r'^dziekujemy/$', ThanksView.as_view(), name='funding_thanks'),
    url(r'^niepowodzenie/$', NoThanksView.as_view(), name='funding_nothanks'),

    url(r'^wylacz_email/$', DisableNotifications.as_view(), name='funding_disable_notifications'),

    url(r'^getpaid/', include('getpaid.urls')),
)
