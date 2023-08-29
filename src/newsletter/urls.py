# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('zapisz-sie/', views.subscribe_form, name='subscribe'),
    path('zapisz-sie/<slug:slug>/', views.subscribe_form, name='subscribe'),
    path('zapis/', views.subscribed, name='subscribed'),
    path('wypisz-sie/', RedirectView.as_view(
            url='https://mailing.mdrn.pl/?p=unsubscribe',
            permanent=False,
        ), name='unsubscribe'),
]
