# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url

from push import views

urlpatterns = (
    url(r'^wyslij/$', views.notification_form, name='notification_form'),
    url(r'^wyslane/$', views.notification_sent, name='notification_sent'),
)
