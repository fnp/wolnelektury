# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path, re_path
from django.db.models import Max
from django.views.generic import ListView, RedirectView
from catalogue.feeds import AudiobookFeed
from catalogue.models import Book
from catalogue import views
import search.views


urlpatterns = [
    # old search page - redirected
    path('szukaj/', RedirectView.as_view(
        url='/szukaj/', query_string=True, permanent=True)),

    path('', views.catalogue, name='catalogue'),

    path('autor/', views.tag_catalogue, {'category': 'author'}, name='author_catalogue'),
    path('epoka/', views.tag_catalogue, {'category': 'epoch'}, name='epoch_catalogue'),
    path('gatunek/', views.tag_catalogue, {'category': 'genre'}, name='genre_catalogue'),
    path('rodzaj/', views.tag_catalogue, {'category': 'kind'}, name='kind_catalogue'),
    path('motyw/', views.tag_catalogue, {'category': 'theme'}, name='theme_catalogue'),

    path('galeria/', views.GalleryView.as_view(), name='gallery'),
    path('kolekcje/', views.collections, name='catalogue_collections'),

    path('lektury/', views.LiteratureView.as_view(), name='book_list'),
    path('lektury/<slug:slug>/', views.collection, name='collection'),
    path('audiobooki/', views.AudiobooksView.as_view(), name='audiobook_list'),
    path('daisy/', views.daisy_list, name='daisy_list'),
    path('jtags/', search.views.hint, {'param': 'q', 'mozhint': True}, name='jhint'),
    path('nowe/', ListView.as_view(
        queryset=Book.objects.filter(parent=None, findable=True).order_by('-created_at')[:100],
        template_name='catalogue/recent_list.html'), name='recent_list'),
    path('nowe/audiobooki/', ListView.as_view(
        queryset=Book.objects.filter(media__type='ogg').annotate(m=Max('media__uploaded_at')).order_by('-m')[:100],
        template_name='catalogue/recent_audiobooks_list.html'), name='recent_audiobooks_list'),
    path('nowe/daisy/', ListView.as_view(
        queryset=Book.objects.filter(media__type='daisy').annotate(m=Max('media__uploaded_at')).order_by('-m')[:100],
        template_name='catalogue/recent_daisy_list.html'), name='recent_daisy_list'),

    path('custompdf/<slug:slug>/', views.CustomPDFFormView(), name='custom_pdf_form'),

    re_path(r'^audiobooki/(?P<type>mp3|ogg|daisy|all).xml$', AudiobookFeed(), name='audiobook_feed'),

    path('pobierz/<key>/<slug:slug>.<slug:format_>', views.embargo_link, name='embargo_link'),

    # zip
    path('zip/pdf.zip', views.download_zip, {'file_format': 'pdf', 'slug': None}, 'download_zip_pdf'),
    path('zip/epub.zip', views.download_zip, {'file_format': 'epub', 'slug': None}, 'download_zip_epub'),
    path('zip/mobi.zip', views.download_zip, {'file_format': 'mobi', 'slug': None}, 'download_zip_mobi'),
    path('zip/mp3/<slug:slug>.zip', views.download_zip, {'media_format': 'mp3'}, 'download_zip_mp3'),
    path('zip/ogg/<slug:slug>.zip', views.download_zip, {'media_format': 'ogg'}, 'download_zip_ogg'),

    # Public interface. Do not change this URLs.
    path('lektura/<slug:slug>.html', views.book_text, name='book_text'),
    path('lektura/<slug:slug>/', views.book_detail, name='book_detail'),
    path('lektura/<slug:slug>/motyw/<slug:theme_slug>/',
         views.book_fragments, name='book_fragments'),

    path('okladka-ridero/<slug:slug>.png', views.ridero_cover),
    path('isbn/<slug:book_format>/<slug:slug>/', views.get_isbn),

    # This should be the last pattern.
    re_path(r'^galeria/(?P<tags>[a-zA-Z0-9-/]*)/$', views.tagged_object_list, {'list_type': 'gallery'},
        name='tagged_object_list_gallery'),
    re_path(r'^audiobooki/(?P<tags>[a-zA-Z0-9-/]*)/$', views.tagged_object_list, {'list_type': 'audiobooks'},
        name='tagged_object_list_audiobooks'),
    re_path(r'^(?P<tags>[a-zA-Z0-9-/]*)/$', views.tagged_object_list, {'list_type': 'books'},
        name='tagged_object_list'),

]
