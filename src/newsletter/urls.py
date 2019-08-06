# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^zapisz-sie/$', views.subscribe_form, name='subscribe'),
    url(r'^zapis/$', views.subscribed, name='subscribed'),
    url(r'^potwierdzenie/(?P<subscription_id>[0-9]+)/(?P<hashcode>[0-9a-f]+)/$',
        views.confirm_subscription, name='confirm_subscription'),
    url(r'^wypisz-sie/$', views.unsubscribe_form, name='unsubscribe'),
    url(r'^wypisano/$', views.unsubscribed, name='unsubscribed'),
]
