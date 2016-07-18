# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^wypisz-sie/$', views.unsubscribe, name='unsubscribe'),
]
