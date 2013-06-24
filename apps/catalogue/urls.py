# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls.defaults import *
from django.db.models import Max
from django.views.generic import ListView, RedirectView
from catalogue.feeds import AudiobookFeed
from catalogue.views import CustomPDFFormView
from catalogue.models import Book


SLUG = r'[a-z0-9-]*'

urlpatterns = patterns('picture.views',
    # pictures - currently pictures are coupled with catalogue, hence the url is here
    url(r'^obraz/?$', 'picture_list'),
    url(r'^obraz/(?P<picture>%s)/?$' % SLUG, 'picture_detail')
)

urlpatterns += patterns('',
    # old search page - redirected
    url(r'^szukaj/$', RedirectView.as_view(
            url='/szukaj/', query_string=True)),
)

urlpatterns += patterns('catalogue.views',
    url(r'^$', 'catalogue', name='catalogue'),

    url(r'^lektury/$', 'book_list', name='book_list'),
    url(r'^lektury/(?P<slug>[a-zA-Z0-9-]+)/$', 'collection', name='collection'),
    url(r'^audiobooki/$', 'audiobook_list', name='audiobook_list'),
    url(r'^daisy/$', 'daisy_list', name='daisy_list'),
    url(r'^tags/$', 'tags_starting_with', name='hint'),
    url(r'^jtags/$', 'json_tags_starting_with', name='jhint'),
    url(r'^nowe/$', ListView.as_view(
        queryset=Book.objects.filter(parent=None).order_by('-created_at'),
        template_name='catalogue/recent_list.html'), name='recent_list'),
    url(r'^nowe/audiobooki/$', ListView.as_view(
        queryset=Book.objects.filter(media__type='ogg').annotate(m=Max('media__uploaded_at')).order_by('-m'),
            template_name='catalogue/recent_audiobooks_list.html'), name='recent_audiobooks_list'),
    url(r'^nowe/daisy/$', ListView.as_view(
        queryset=Book.objects.filter(media__type='daisy').annotate(m=Max('media__uploaded_at')).order_by('-m'),
            template_name='catalogue/recent_daisy_list.html'), name='recent_daisy_list'),

    url(r'^custompdf/(?P<slug>%s)/$' % SLUG, CustomPDFFormView(), name='custom_pdf_form'),

    url(r'^audiobooki/(?P<type>mp3|ogg|daisy|all).xml$', AudiobookFeed(), name='audiobook_feed'),


    # zip
    url(r'^zip/pdf\.zip$', 'download_zip', {'format': 'pdf', 'slug': None}, 'download_zip_pdf'),
    url(r'^zip/epub\.zip$', 'download_zip', {'format': 'epub', 'slug': None}, 'download_zip_epub'),
    url(r'^zip/mobi\.zip$', 'download_zip', {'format': 'mobi', 'slug': None}, 'download_zip_mobi'),
    url(r'^zip/mp3/(?P<slug>%s)\.zip' % SLUG, 'download_zip', {'format': 'mp3'}, 'download_zip_mp3'),
    url(r'^zip/ogg/(?P<slug>%s)\.zip' % SLUG, 'download_zip', {'format': 'ogg'}, 'download_zip_ogg'),

    # Public interface. Do not change this URLs.
    url(r'^lektura/(?P<slug>%s)\.html$' % SLUG, 'book_text', name='book_text'),
    url(r'^lektura/(?P<slug>%s)/audiobook/$' % SLUG, 'player', name='book_player'),
    url(r'^lektura/(?P<slug>%s)/$' % SLUG, 'book_detail', name='book_detail'),
    url(r'^lektura/(?P<slug>%s)/motyw/(?P<theme_slug>[a-zA-Z0-9-]+)/$' % SLUG,
        'book_fragments', name='book_fragments'),

    # This should be the last pattern.
    url(r'^(?P<tags>[a-zA-Z0-9-/]*)/$', 'tagged_object_list', name='tagged_object_list'),
)
