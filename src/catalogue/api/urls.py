# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path, re_path
from stats.utils import piwik_track_view
from . import views


tags_re = r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){0,6})'
paginate_re = r'(?:after/(?P<after>[a-z0-9-]+)/)?(?:count/(?P<count>[0-9]+)/)?$'


urlpatterns = [
    # books by collections
    path('collections/',
         piwik_track_view(views.CollectionList.as_view()),
         name="catalogue_api_collections"),
    path('collections/<slug:slug>/',
         piwik_track_view(views.CollectionDetail.as_view()),
         name="collection-detail"),

    re_path(tags_re + r'books/' + paginate_re,
            piwik_track_view(views.BookList.as_view()),
            {"filename": "books"}, name='catalogue_api_book_list'),
    re_path(tags_re + r'parent_books/' + paginate_re,
            piwik_track_view(views.BookList.as_view()),
            {"filename": "parent_books", "top_level": True}, name='catalogue_api_parent_book_list'),
    re_path(tags_re + r'audiobooks/' + paginate_re,
            piwik_track_view(views.BookList.as_view()),
            {"filename": "audiobooks", "audiobooks": True}, name='catalogue_api_audiobook_list'),
    re_path(tags_re + r'daisy/' + paginate_re,
            piwik_track_view(views.BookList.as_view()),
            {"filename": "daisy", "daisy": True}, name='catalogue_api_daisy_list'),
    re_path(r'^recommended/' + paginate_re,
            piwik_track_view(views.BookList.as_view()),
            {"recommended": True}, name='catalogue_api_recommended_list'),
    path('newest/',
         piwik_track_view(views.BookList.as_view()),
         {"newest": True, "top_level": True, "count": 20},
         name='catalogue_api_newest_list'),

    path('books/<slug:slug>/',
         piwik_track_view(views.BookDetail.as_view()),
         name='catalogue_api_book'),

    re_path(tags_re + r'ebooks/' + paginate_re,
            piwik_track_view(views.EbookList.as_view()),
            name='catalogue_api_ebook_list'),
    re_path(tags_re + r'parent_ebooks/' + paginate_re,
            piwik_track_view(views.EbookList.as_view()),
            {"top_level": True},
            name='catalogue_api_parent_ebook_list'),

    path('filter-books/',
         piwik_track_view(views.FilterBookList.as_view()),
         name='catalogue_api_filter_books'),

    path('epub/<slug:slug>/',
         piwik_track_view(views.EpubView.as_view()),
         name='catalogue_api_epub'),

    path('preview/',
         piwik_track_view(views.Preview.as_view()),
         name='catalogue_api_preview'),

    re_path(r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){1,6})fragments/$',
            piwik_track_view(views.FragmentList.as_view())),
    path('books/<slug:book>/fragments/<slug:anchor>/',
         piwik_track_view(views.FragmentView.as_view()),
         name="catalogue_api_fragment"),

    path('<slug:category>s/',
         piwik_track_view(views.TagCategoryView.as_view()),
         name='catalogue_api_tag_list'),
    path('<slug:category>s/<slug:slug>/',
         piwik_track_view(views.TagView.as_view()),
         name="catalogue_api_tag"),
]
