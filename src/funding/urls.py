# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url, include

from .views import (WLFundView, OfferDetailView, OfferListView,
                ThanksView, NoThanksView, CurrentView, DisableNotifications)


urlpatterns = patterns('funding.views',

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

    # Includes
    url(r'^o/(?P<pk>\d+)/top-bar\.(?P<lang>.+)\.html$', 'top_bar', name='funding_top_bar'),
    url(r'^o/(?P<pk>\d+)/detail-bar\.(?P<lang>.+)\.html$', 'detail_bar', name='funding_detail_bar'),
    url(r'^o/(?P<pk>\d+)/list-bar\.(?P<lang>.+)\.html$', 'list_bar', name='funding_list_bar'),
    url(r'^o/(?P<pk>\d+)/status\.(?P<lang>.+)\.html$', 'offer_status', name='funding_status'),
    url(r'^o/(?P<pk>\d+)/status-more\.(?P<lang>.+)\.html$', 'offer_status_more', name='funding_status_more'),
    url(r'^o/(?P<pk>\d+)/fundings/(?P<page>\d+)\.(?P<lang>.+)\.html$', 'offer_fundings', name='funding_fundings'),
)
