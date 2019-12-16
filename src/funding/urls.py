# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.CurrentView.as_view(), name='funding_current'),
    path('teraz/', views.CurrentView.as_view()),
    path('teraz/<slug:slug>/', views.CurrentView.as_view(), name='funding_current'),
    path('lektura/', views.OfferListView.as_view(), name='funding'),
    path('lektura/<slug:slug>/', views.OfferDetailView.as_view(), name='funding_offer'),
    path('pozostale/', views.WLFundView.as_view(), name='funding_wlfund'),

    path('dziekujemy/', views.ThanksView.as_view(), name='funding_thanks'),
    path('niepowodzenie/', views.NoThanksView.as_view(), name='funding_nothanks'),

    path('wylacz_email/', views.DisableNotifications.as_view(), name='funding_disable_notifications'),

    path('getpaid/', include('getpaid.urls')),
]
