# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from django.db.models import Max
from django.views.generic import ListView, RedirectView
from catalogue.feeds import AudiobookFeed
from catalogue.models import Book
from catalogue import views
import picture.views


SLUG = r'[a-z0-9-]*'

urlpatterns = [
    url(r'^obraz/strona/$', picture.views.picture_page, name='picture_page'),
    # pictures - currently pictures are coupled with catalogue, hence the url is here
    url(r'^obraz/$', picture.views.picture_list_thumb, name='picture_list_thumb'),
    url(r'^obraz/(?P<slug>%s).html$' % SLUG, picture.views.picture_viewer, name='picture_viewer'),
    url(r'^obraz/(?P<slug>%s)/$' % SLUG, picture.views.picture_detail),

    url(r'^p/(?P<pk>\d+)/mini\.(?P<lang>.+)\.html', picture.views.picture_mini, name='picture_mini'),
    url(r'^p/(?P<pk>\d+)/short\.(?P<lang>.+)\.html', picture.views.picture_short, name='picture_short'),
    url(r'^pa/(?P<pk>\d+)/short\.(?P<lang>.+)\.html', picture.views.picturearea_short, name='picture_area_short'),

    # old search page - redirected
    url(r'^szukaj/$', RedirectView.as_view(
            url='/szukaj/', query_string=True, permanent=True)),

    url(r'^$', views.catalogue, name='catalogue'),

    url(r'^autor/$', views.tag_catalogue, {'category': 'author'}, name='author_catalogue'),
    url(r'^epoka/$', views.tag_catalogue, {'category': 'epoch'}, name='epoch_catalogue'),
    url(r'^gatunek/$', views.tag_catalogue, {'category': 'genre'}, name='genre_catalogue'),
    url(r'^rodzaj/$', views.tag_catalogue, {'category': 'kind'}, name='kind_catalogue'),
    url(r'^motyw/$', views.tag_catalogue, {'category': 'theme'}, name='theme_catalogue'),

    url(r'^galeria/$', views.gallery, name='gallery'),
    url(r'^kolekcje/$', views.collections, name='catalogue_collections'),

    url(r'^lektury/$', views.literature, name='book_list'),
    url(r'^lektury/(?P<slug>[a-zA-Z0-9-]+)/$', views.collection, name='collection'),
    url(r'^audiobooki/$', views.audiobooks, name='audiobook_list'),
    url(r'^daisy/$', views.daisy_list, name='daisy_list'),
    url(r'^nowe/$', ListView.as_view(
        queryset=Book.objects.filter(parent=None).order_by('-created_at'),
        template_name='catalogue/recent_list.html'), name='recent_list'),
    url(r'^nowe/audiobooki/$', ListView.as_view(
        queryset=Book.objects.filter(media__type='ogg').annotate(m=Max('media__uploaded_at')).order_by('-m'),
        template_name='catalogue/recent_audiobooks_list.html'), name='recent_audiobooks_list'),
    url(r'^nowe/daisy/$', ListView.as_view(
        queryset=Book.objects.filter(media__type='daisy').annotate(m=Max('media__uploaded_at')).order_by('-m'),
        template_name='catalogue/recent_daisy_list.html'), name='recent_daisy_list'),

    url(r'^custompdf/(?P<slug>%s)/$' % SLUG, views.CustomPDFFormView(), name='custom_pdf_form'),

    url(r'^audiobooki/(?P<type>mp3|ogg|daisy|all).xml$', AudiobookFeed(), name='audiobook_feed'),

    url(r'^pobierz/(?P<slug>%s).(?P<format_>[a-z0-9]*)$' % SLUG, views.embargo_link, name='embargo_link'),

    # zip
    url(r'^zip/pdf\.zip$', views.download_zip, {'format': 'pdf', 'slug': None}, 'download_zip_pdf'),
    url(r'^zip/epub\.zip$', views.download_zip, {'format': 'epub', 'slug': None}, 'download_zip_epub'),
    url(r'^zip/mobi\.zip$', views.download_zip, {'format': 'mobi', 'slug': None}, 'download_zip_mobi'),
    url(r'^zip/mp3/(?P<slug>%s)\.zip' % SLUG, views.download_zip, {'format': 'mp3'}, 'download_zip_mp3'),
    url(r'^zip/ogg/(?P<slug>%s)\.zip' % SLUG, views.download_zip, {'format': 'ogg'}, 'download_zip_ogg'),

    # Public interface. Do not change this URLs.
    url(r'^lektura/(?P<slug>%s)\.html$' % SLUG, views.book_text, name='book_text'),
    url(r'^lektura/(?P<slug>%s)/audiobook/$' % SLUG, views.player, name='book_player'),
    url(r'^lektura/(?P<slug>%s)/$' % SLUG, views.book_detail, name='book_detail'),
    url(r'^lektura/(?P<slug>%s)/motyw/(?P<theme_slug>[a-zA-Z0-9-]+)/$' % SLUG,
        views.book_fragments, name='book_fragments'),

    url(r'^okladka-ridero/(?P<slug>%s).png$' % SLUG, views.ridero_cover),
    url(r'^isbn/(?P<book_format>(pdf|epub|mobi|txt|html))/(?P<slug>%s)/' % SLUG, views.get_isbn),

    # Includes.
    url(r'^b/(?P<pk>\d+)/mini\.(?P<lang>.+)\.html', views.book_mini, name='catalogue_book_mini'),
    url(r'^b/(?P<pk>\d+)/mini_nolink\.(?P<lang>.+)\.html', views.book_mini, {'with_link': False},
        name='catalogue_book_mini_nolink'),
    url(r'^b/(?P<pk>\d+)/short\.(?P<lang>.+)\.html', views.book_short, name='catalogue_book_short'),
    url(r'^b/(?P<pk>\d+)/wide\.(?P<lang>.+)\.html', views.book_wide, name='catalogue_book_wide'),
    url(r'^f/(?P<pk>\d+)/promo\.(?P<lang>.+)\.html', views.fragment_promo, name='catalogue_fragment_promo'),
    url(r'^f/(?P<pk>\d+)/short\.(?P<lang>.+)\.html', views.fragment_short, name='catalogue_fragment_short'),
    url(r'^t/(?P<pk>\d+)/box\.(?P<lang>.+)\.html', views.tag_box, name='catalogue_tag_box'),
    url(r'^c/(?P<pk>.+)/box\.(?P<lang>.+)\.html', views.collection_box, name='catalogue_collection_box'),

    # This should be the last pattern.
    url(r'^galeria/(?P<tags>[a-zA-Z0-9-/]*)/$', views.tagged_object_list, {'list_type': 'gallery'},
        name='tagged_object_list_gallery'),
    url(r'^audiobooki/(?P<tags>[a-zA-Z0-9-/]*)/$', views.tagged_object_list, {'list_type': 'audiobooks'},
        name='tagged_object_list_audiobooks'),
    url(r'^(?P<tags>[a-zA-Z0-9-/]*)/$', views.tagged_object_list, {'list_type': 'books'},
        name='tagged_object_list'),
]
