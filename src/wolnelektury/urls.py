# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic import RedirectView
import django.views.static
from migdal.urls import urlpatterns as migdal_urlpatterns
import catalogue.views
import picture.views
from . import views


urlpatterns = [
    url(r'^$', views.main_page, name='main_page'),
    url(r'^planowane/$', views.publish_plan, name='publish_plan'),
    url(r'^widget\.html$', views.widget, name='widget'),

    url(r'^zegar/$', views.clock, name='clock'),

    # Authentication
    url(r'^uzytkownik/$', views.user_settings, name='user_settings'),
    url(r'^uzytkownik/login/$', views.LoginFormView(), name='login'),
    url(r'^uzytkownik/signup/$', views.RegisterFormView(), name='register'),
    url(r'^uzytkownik/logout/$', views.logout_then_redirect, name='logout'),
    url(r'^uzytkownik/zaloguj-utworz/$', views.LoginRegisterFormView(), name='login_register'),
    url(r'^uzytkownik/social/signup/$', views.SocialSignupView.as_view(), name='socialaccount_signup'),

    # Includes.
    url(r'^latests_blog_posts.html$', views.latest_blog_posts, name='latest_blog_posts'),
]

urlpatterns += [
    url(r'^katalog/', include('catalogue.urls')),
    url(r'^opds/', include('opds.urls')),
    url(r'^sugestia/', include('suggest.urls')),
    url(r'^lesmianator/', include('lesmianator.urls')),
    url(r'^przypisy/', include('dictionary.urls')),
    url(r'^raporty/', include('reporting.urls')),
    url(r'^info/', include('infopages.urls')),
    url(r'^ludzie/', include('social.urls')),
    url(r'^uzytkownik/', include('allauth.urls')),
    url(r'^czekaj/', include('waiter.urls')),
    url(r'^wesprzyj/', include('funding.urls')),
    url(r'^ankieta/', include('polls.urls')),
    url(r'^biblioteki/', include('libraries.urls')),
    url(r'^chunks/', include('chunks.urls')),
    url(r'^sponsors/', include('sponsors.urls')),
    url(r'^newsletter/', include('newsletter.urls')),
    url(r'^formularz/', include('contact.urls')),
    url(r'^isbn/', include('isbn.urls')),
    url(r'^paypal/', include('paypal.urls')),

    # Admin panel
    url(r'^admin/catalogue/book/import$', catalogue.views.import_book, name='import_book'),
    url(r'^admin/catalogue/picture/import$', picture.views.import_picture, name='import_picture'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # API
    url(r'^api/', include('api.urls')),
    # OAIPMH
    url(r'^oaipmh/', include('oai.urls')),

    url(r'^szukaj/', include('search.urls')),

    # Static files
    url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:], django.views.static.serve,
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += [
    # old static pages - redirected
    url(r'^1procent/$', RedirectView.as_view(
        url='http://nowoczesnapolska.org.pl/wesprzyj_nas/', permanent=True)),
    url(r'^epub/$', RedirectView.as_view(
        url='/katalog/lektury/', permanent=False)),
    url(r'^mozesz-nam-pomoc/$', RedirectView.as_view(
        url='/info/wlacz-sie-w-prace/', permanent=True)),
    url(r'^o-projekcie/$', RedirectView.as_view(
        url='/info/o-projekcie/', permanent=True)),
    url(r'^widget/$', RedirectView.as_view(
        url='/info/widget/', permanent=True)),
    url(r'^wolontariat/$', RedirectView.as_view(
        url='/info/wlacz-sie-w-prace/', permanent=False)),
]

urlpatterns += [
    url(r'^error-test/$', views.exception_test),
    # url(r'^post-test/$', views.post_test),
]

urlpatterns += migdal_urlpatterns
