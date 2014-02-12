# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^set_language/$', 'django.views.i18n.set_language', {},
        name='set_language'),
)
