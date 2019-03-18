# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from django.views.generic import RedirectView
from . import views

urlpatterns = (
    url(r'^form/$', RedirectView.as_view(url='/towarzystwo/dolacz/')),
    url(r'^app-form/$', RedirectView.as_view(url='/towarzystwo/dolacz/app/')),

    url(r'^return/$', views.paypal_return, name='paypal_return'),
    url(r'^app-return/$', views.paypal_return, kwargs={'app': True}, name='paypal_app_return'),
    url(r'^cancel/$', views.paypal_cancel, name='paypal_cancel'),
)
