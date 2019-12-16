# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from push import views


urlpatterns = [
    path('wyslij/', views.notification_form, name='notification_form'),
    path('wyslane/', views.notification_sent, name='notification_sent'),
]
