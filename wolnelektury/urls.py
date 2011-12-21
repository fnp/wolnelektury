# -*- coding: utf-8 -*-
import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
import views


admin.autodiscover()

urlpatterns = patterns('wolnelektury.views',
    url(r'^$', 'main_page', name='main_page'),

    url(r'^zegar/$', 'clock', name='clock'),

    # Authentication
    url(r'^uzytkownicy/zaloguj/$', views.LoginFormView(), name='login'),
    url(r'^uzytkownicy/utworz/$', views.RegisterFormView(), name='register'),
    url(r'^uzytkownicy/wyloguj/$', 'logout_then_redirect', name='logout'),
)

urlpatterns += patterns('',
    url(r'^katalog/', include('catalogue.urls')),
    url(r'^materialy/', include('lessons.urls')),
    url(r'^opds/', include('opds.urls')),
    url(r'^sugestia/', include('suggest.urls')),
    url(r'^lesmianator/', include('lesmianator.urls')),
    url(r'^przypisy/', include('dictionary.urls')),
    url(r'^raporty/', include('reporting.urls')),
    url(r'^info/', include('infopages.urls')),

    # Admin panel
    url(r'^admin/catalogue/book/import$', 'catalogue.views.import_book', name='import_book'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # API
    (r'^api/', include('api.urls')),

    url(r'^newsearch/', include('search.urls')),

    # Static files
    url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += patterns('django.views.generic.simple',
    # old static pages - redirected
    url(r'^1procent/$', 'redirect_to',
        {'url': 'http://nowoczesnapolska.org.pl/wesprzyj_nas/'}),
    url(r'^epub/$', 'redirect_to',
        {'url': '/katalog/lektury/'}),
    url(r'^mozesz-nam-pomoc/$', 'redirect_to',
        {'url': '/info/mozesz-nam-pomoc'}),
    url(r'^o-projekcie/$', 'redirect_to',
        {'url': '/info/o-projekcie'}),
    url(r'^widget/$', 'redirect_to',
        {'url': '/info/widget'}),
    url(r'^wolontariat/$', 'redirect_to',
        {'url': '/info/mozesz-nam-pomoc/'}),
)
    

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
