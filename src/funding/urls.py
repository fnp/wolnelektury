# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^$', views.CurrentView.as_view(), name='funding_current'),
    url(r'^teraz/$', views.CurrentView.as_view()),
    url(r'^teraz/(?P<slug>[^/]+)/$', views.CurrentView.as_view(), name='funding_current'),
    url(r'^lektura/$', views.OfferListView.as_view(), name='funding'),
    url(r'^lektura/(?P<slug>[^/]+)/$', views.OfferDetailView.as_view(), name='funding_offer'),
    url(r'^pozostale/$', views.WLFundView.as_view(), name='funding_wlfund'),

    url(r'^dziekujemy/$', views.ThanksView.as_view(), name='funding_thanks'),
    url(r'^niepowodzenie/$', views.NoThanksView.as_view(), name='funding_nothanks'),

    url(r'^wylacz_email/$', views.DisableNotifications.as_view(), name='funding_disable_notifications'),

    url(r'^getpaid/', include('getpaid.urls')),
]
