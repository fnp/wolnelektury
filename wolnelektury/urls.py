# -*- coding: utf-8 -*-
import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from catalogue.forms import SearchForm

from infopages.models import InfoPage


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^katalog/', include('catalogue.urls')),
    url(r'^materialy/', include('lessons.urls')),
    url(r'^opds/', include('opds.urls')),
    url(r'^sugestia/', include('suggest.urls')),
    url(r'^lesmianator/', include('lesmianator.urls')),
    url(r'^przypisy/', include('dictionary.urls')),

    # Static pages
    url(r'^mozesz-nam-pomoc/$', 'infopages.views.infopage', {'slug': 'help_us'}, name='help_us'),
    url(r'^o-projekcie/$', 'infopages.views.infopage', {'slug': 'about_us'}, name='about_us'),
    url(r'^widget/$', 'infopages.views.infopage', {'slug': 'widget'}, name='widget'),

    # Admin panel
    url(r'^admin/catalogue/book/import$', 'catalogue.views.import_book', name='import_book'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Authentication
    url(r'^uzytkownicy/zaloguj/$', 'catalogue.views.login', name='login'),
    url(r'^uzytkownicy/wyloguj/$', 'catalogue.views.logout_then_redirect', name='logout'),
    url(r'^uzytkownicy/utworz/$', 'catalogue.views.register', name='register'),

    # API
    (r'^api/', include('api.urls')),

    # Static files
    url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': 'katalog/'}),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += patterns('django.views.generic.simple',
    # old static pages - redirected
    (r'^1procent/$', 'redirect_to', {'url': 'http://nowoczesnapolska.org.pl/wesprzyj_nas/'}),
    (r'^wolontariat/$', 'redirect_to', {'url': '/mozesz-nam-pomoc/'}),
    (r'^epub/$', 'redirect_to', {'url': '/katalog/lektury/'}),
)
    

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
