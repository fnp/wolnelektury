# -*- coding: utf-8 -*-
import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.generic import RedirectView
import wolnelektury_core.views


admin.autodiscover()

urlpatterns = patterns('wolnelektury_core.views',
    url(r'^$', 'main_page', name='main_page'),
    url(r'^planowane/$', 'publish_plan', name='publish_plan'),

    url(r'^zegar/$', 'clock', name='clock'),

    # Authentication
    url(r'^uzytkownik/$', 'user_settings', name='user_settings'),
    url(r'^uzytkownik/login/$', wolnelektury_core.views.LoginFormView(), name='login'),
    url(r'^uzytkownik/signup/$', wolnelektury_core.views.RegisterFormView(), name='register'),
    url(r'^uzytkownik/logout/$', 'logout_then_redirect', name='logout'),
    url(r'^uzytkownik/zaloguj-utworz/$', wolnelektury_core.views.LoginRegisterFormView(), name='login_register'),
)

urlpatterns += patterns('',
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
    url(r'^biblioteki', include('libraries.urls')),

    # Admin panel
    url(r'^admin/catalogue/book/import$', 'catalogue.views.import_book', name='import_book'),
    url(r'^admin/catalogue/picture/import$', 'picture.views.import_picture', name='import_picture'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # API
    (r'^api/', include('api.urls')),
    # OAIPMH
    (r'^oaipmh/', include('oai.urls')),

    url(r'^szukaj/', include('search.urls')),

    # Static files
    url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += patterns('',
    # old static pages - redirected
    url(r'^1procent/$', RedirectView.as_view(
        url='http://nowoczesnapolska.org.pl/wesprzyj_nas/')),
    url(r'^epub/$', RedirectView.as_view(
        url='/katalog/lektury/')),
    url(r'^mozesz-nam-pomoc/$', RedirectView.as_view(
        url='/info/mozesz-nam-pomoc')),
    url(r'^o-projekcie/$', RedirectView.as_view(
        url='/info/o-projekcie')),
    url(r'^widget/$', RedirectView.as_view(
        url='/info/widget')),
    url(r'^wolontariat/$', RedirectView.as_view(
        url='/info/mozesz-nam-pomoc/')),
)
    

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
