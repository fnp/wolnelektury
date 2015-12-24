# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url
from django.db.models import Max
from django.views.generic import ListView, RedirectView
from catalogue.feeds import AudiobookFeed
from catalogue.views import CustomPDFFormView
from catalogue.models import Book


SLUG = r'[a-z0-9-]*'

urlpatterns = patterns('picture.views',
    # pictures - currently pictures are coupled with catalogue, hence the url is here
    url(r'^obraz/$', 'picture_list_thumb', name='picture_list_thumb'),
    url(r'^obraz/(?P<slug>%s).html$' % SLUG, 'picture_viewer', name='picture_viewer'),
    url(r'^obraz/(?P<slug>%s)/$' % SLUG, 'picture_detail'),

    url(r'^p/(?P<pk>\d+)/mini\.(?P<lang>.+)\.html', 'picture_mini', name='picture_mini'),
    url(r'^p/(?P<pk>\d+)/short\.(?P<lang>.+)\.html', 'picture_short', name='picture_short'),
    url(r'^pa/(?P<pk>\d+)/short\.(?P<lang>.+)\.html', 'picturearea_short', name='picture_area_short'),
)

urlpatterns += patterns('',
    # old search page - redirected
    url(r'^szukaj/$', RedirectView.as_view(
            url='/szukaj/', query_string=True, permanent=True)),
)

urlpatterns += patterns('catalogue.views',
    url(r'^$', 'catalogue', name='catalogue'),

    url(r'^lektury/$', 'book_list', name='book_list'),
    url(r'^lektury/(?P<slug>[a-zA-Z0-9-]+)/$', 'collection', name='collection'),
    url(r'^audiobooki/$', 'audiobook_list', name='audiobook_list'),
    url(r'^daisy/$', 'daisy_list', name='daisy_list'),
    url(r'^tags/$', 'tags_starting_with', name='hint'),
    url(r'^jtags/?$', 'json_tags_starting_with', name='jhint'),
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

    # Includes.
    url(r'^(?P<lang>[^/]+)\.json$', 'catalogue_json'),
    url(r'^b/(?P<pk>\d+)/mini\.(?P<lang>.+)\.html', 'book_mini', name='catalogue_book_mini'),
    url(r'^b/(?P<pk>\d+)/mini_nolink\.(?P<lang>.+)\.html', 'book_mini', {'with_link': False}, name='catalogue_book_mini_nolink'),
    url(r'^b/(?P<pk>\d+)/short\.(?P<lang>.+)\.html', 'book_short', name='catalogue_book_short'),
    url(r'^b/(?P<pk>\d+)/wide\.(?P<lang>.+)\.html', 'book_wide', name='catalogue_book_wide'),
    url(r'^f/(?P<pk>\d+)/promo\.(?P<lang>.+)\.html', 'fragment_promo', name='catalogue_fragment_promo'),
    url(r'^f/(?P<pk>\d+)/short\.(?P<lang>.+)\.html', 'fragment_short', name='catalogue_fragment_short'),

    # This should be the last pattern.
    url(r'^(?P<tags>[a-zA-Z0-9-/]*)/$', 'tagged_object_list', name='tagged_object_list'),
)
