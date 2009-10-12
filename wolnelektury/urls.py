# -*- coding: utf-8 -*-
import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from catalogue.forms import SearchForm


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^katalog/', include('catalogue.urls')),
    
    # Static pages
    url(r'^wolontariat/$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'info/voluntary_services.html', 'extra_context': {'form': SearchForm()}},
        name='voluntary_services'),
    url(r'^mozesz-nam-pomoc/$', 'django.views.generic.simple.direct_to_template',
        {'template': 'info/help_us.html', 'extra_context': {'form': SearchForm()}},
        name='help_us'),
    url(r'^o-projekcie/$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'info/about_us.html', 'extra_context': {'form': SearchForm()}},
        name='about_us'),
    
    # Admin panel
    url(r'^admin/catalogue/book/import$', 'catalogue.views.import_book', name='import_book'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/(.*)$', admin.site.root),
    
    # Authentication
    url(r'^uzytkownicy/zaloguj/$', 'catalogue.views.login', name='login'),
    url(r'^uzytkownicy/wyloguj/$', 'catalogue.views.logout_then_redirect', name='logout'),
    url(r'^uzytkownicy/utworz/$', 'catalogue.views.register', name='register'),
    
    # Static files
    url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': 'katalog/'}),
)
