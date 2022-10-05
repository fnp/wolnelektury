# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path, include
from annoy.utils import banner_exempt
from . import views


urlpatterns = [
    path('', banner_exempt(views.CurrentView.as_view()), name='funding_current'),
    path('teraz/', banner_exempt(views.CurrentView.as_view())),
    path('teraz/<slug:slug>/', banner_exempt(views.CurrentView.as_view()), name='funding_current'),
    path('lektura/', banner_exempt(views.OfferListView.as_view()), name='funding'),
    path('lektura/<slug:slug>/', banner_exempt(views.OfferDetailView.as_view()), name='funding_offer'),
    path('pozostale/', banner_exempt(views.WLFundView.as_view()), name='funding_wlfund'),

    path('dziekujemy/', banner_exempt(views.ThanksView.as_view()), name='funding_thanks'),
    path('niepowodzenie/', banner_exempt(views.NoThanksView.as_view()), name='funding_nothanks'),

    path('wylacz_email/', banner_exempt(views.DisableNotifications.as_view()), name='funding_disable_notifications'),
    path('przylacz/<key>/', banner_exempt(views.claim), name='funding_claim'),

    path('notify/<int:pk>/', views.PayUNotifyView.as_view(), name='funding_payu_notify'),
]
