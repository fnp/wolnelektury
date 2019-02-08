# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
from django.http import Http404, HttpResponse
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework import status
from paypal.permissions import IsSubscribed
from api.handlers import read_tags
from .helpers import books_after, order_books
from . import serializers
from catalogue.forms import BookImportForm
from catalogue.models import Book, Collection, Tag, Fragment
from catalogue.models.tag import prefetch_relations
from wolnelektury.utils import re_escape


book_tag_categories = ['author', 'epoch', 'kind', 'genre']


class CollectionList(ListAPIView):
    queryset = Collection.objects.all()
    serializer_class = serializers.CollectionListSerializer


class CollectionDetail(RetrieveAPIView):
    queryset = Collection.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.CollectionSerializer


class BookList(ListAPIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = Book.objects.none()  # Required for DjangoModelPermissions
    serializer_class = serializers.BookListSerializer

    def get_queryset(self):
        try:
            tags, ancestors = read_tags(
                self.kwargs.get('tags', ''), self.request,
                allowed=('author', 'epoch', 'kind', 'genre')
            )
        except ValueError:
            raise Http404

        new_api = self.request.query_params.get('new_api')
        after = self.request.query_params.get('after', self.kwargs.get('after'))
        count = self.request.query_params.get('count', self.kwargs.get('count'))

        if tags:
            if self.kwargs.get('top_level'):
                books = Book.tagged_top_level(tags)
                if not books:
                    raise Http404
                return books
            else:
                books = Book.tagged.with_all(tags)
        else:
            books = Book.objects.all()
        books = order_books(books, new_api)

        if self.kwargs.get('top_level'):
            books = books.filter(parent=None)
        if self.kwargs.get('audiobooks'):
            books = books.filter(media__type='mp3').distinct()
        if self.kwargs.get('daisy'):
            books = books.filter(media__type='daisy').distinct()
        if self.kwargs.get('recommended'):
            books = books.filter(recommended=True)
        if self.kwargs.get('newest'):
            books = books.order_by('-created_at')

        if after:
            books = books_after(books, after, new_api)

        prefetch_relations(books, 'author')
        prefetch_relations(books, 'genre')
        prefetch_relations(books, 'kind')
        prefetch_relations(books, 'epoch')

        if count:
            books = books[:count]

        return books

    def post(self, request, **kwargs):
        # Permission needed.
        data = json.loads(request.POST.get('data'))
        form = BookImportForm(data)
        if form.is_valid():
            form.save()
            return Response({}, status=status.HTTP_201_CREATED)
        else:
            raise Http404


class BookDetail(RetrieveAPIView):
    queryset = Book.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.BookDetailSerializer


class EbookList(BookList):
    serializer_class = serializers.EbookSerializer


class Preview(ListAPIView):
    queryset = Book.objects.filter(preview=True)
    serializer_class = serializers.BookPreviewSerializer


class FilterBookList(ListAPIView):
    serializer_class = serializers.FilterBookListSerializer

    def parse_bool(self, s):
        if s in ('true', 'false'):
            return s == 'true'
        else:
            return None

    def get_queryset(self):
        key_sep = '$'
        search_string = self.request.query_params.get('search')
        is_lektura = self.parse_bool(self.request.query_params.get('lektura'))
        is_audiobook = self.parse_bool(self.request.query_params.get('audiobook'))
        preview = self.parse_bool(self.request.query_params.get('preview'))

        new_api = self.request.query_params.get('new_api')
        after = self.request.query_params.get('after')
        count = int(self.request.query_params.get('count', 50))
        books = order_books(Book.objects.distinct(), new_api)
        if is_lektura is not None:
            books = books.filter(has_audience=is_lektura)
        if is_audiobook is not None:
            if is_audiobook:
                books = books.filter(media__type='mp3')
            else:
                books = books.exclude(media__type='mp3')
        if preview is not None:
            books = books.filter(preview=preview)
        for category in book_tag_categories:
            category_plural = category + 's'
            if category_plural in self.request.query_params:
                slugs = self.request.query_params[category_plural].split(',')
                tags = Tag.objects.filter(category=category, slug__in=slugs)
                books = Book.tagged.with_any(tags, books)
        if (search_string is not None) and len(search_string) < 3:
            search_string = None
        if search_string:
            search_string = re_escape(search_string)
            books_author = books.filter(cached_author__iregex=r'\m' + search_string)
            books_title = books.filter(title__iregex=r'\m' + search_string)
            books_title = books_title.exclude(id__in=list(books_author.values_list('id', flat=True)))
            if after and (key_sep in after):
                which, key = after.split(key_sep, 1)
                if which == 'title':
                    book_lists = [(books_after(books_title, key, new_api), 'title')]
                else:  # which == 'author'
                    book_lists = [(books_after(books_author, key, new_api), 'author'), (books_title, 'title')]
            else:
                book_lists = [(books_author, 'author'), (books_title, 'title')]
        else:
            if after and key_sep in after:
                which, key = after.split(key_sep, 1)
                books = books_after(books, key, new_api)
            book_lists = [(books, 'book')]

        filtered_books = []
        for book_list, label in book_lists:
            for category in book_tag_categories:
                book_list = prefetch_relations(book_list, category)
            remaining_count = count - len(filtered_books)
            for book in book_list[:remaining_count]:
                book.key = '%s%s%s' % (
                    label, key_sep, book.slug if not new_api else book.full_sort_key())
                filtered_books.append(book)
            if len(filtered_books) == count:
                break

        return filtered_books


class EpubView(RetrieveAPIView):
    queryset = Book.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsSubscribed]

    def get(self, *args, **kwargs):
        return HttpResponse(self.get_object().get_media('epub'))


class TagCategoryView(ListAPIView):
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        category = self.kwargs['category']
        tags = Tag.objects.filter(category=category).exclude(items=None).order_by('slug')
        if self.request.query_params.get('book_only') == 'true':
            tags = tags.filter(for_books=True)
        if self.request.GET.get('picture_only') == 'true':
            tags = filter(for_pictures=True)

        after = self.request.query_params.get('after')
        count = self.request.query_params.get('count')
        if after:
            tags = tags.filter(slug__gt=after)
        if count:
            tags = tags[:count]

        return tags


class TagView(RetrieveAPIView):
    serializer_class = serializers.TagDetailSerializer

    def get_object(self):
        return get_object_or_404(
            Tag,
            category=self.kwargs['category'],
            slug=self.kwargs['slug']
        )


class FragmentList(ListAPIView):
    serializer_class = serializers.FragmentSerializer

    def get_queryset(self):
        try:
            tags, ancestors = read_tags(
                self.kwargs['tags'],
                self.request,
                allowed={'author', 'epoch', 'kind', 'genre', 'book', 'theme'}
            )
        except ValueError:
            raise Http404
        return Fragment.tagged.with_all(tags).select_related('book')


class FragmentView(RetrieveAPIView):
    serializer_class = serializers.FragmentDetailSerializer

    def get_object(self):
        return get_object_or_404(
            Fragment,
            book__slug=self.kwargs['book'],
            anchor=self.kwargs['anchor']
        )