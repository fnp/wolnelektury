# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views

urlpatterns = [
    path('zapisz-sie/', views.subscribe_form, name='subscribe'),
    path('zapisz-sie/konkurs/', views.subscribe_form, {"title": "Zapisz się na newsletter Konkursu", "mailing_list": "contest"}, name='subscribe-contest'),
    path('zapis/', views.subscribed, name='subscribed'),
    path('potwierdzenie/<int:subscription_id>/<slug:hashcode>/',
        views.confirm_subscription, name='confirm_subscription'),
    path('wypisz-sie/', views.unsubscribe_form, name='unsubscribe'),
    path('wypisano/', views.unsubscribed, name='unsubscribed'),
]
