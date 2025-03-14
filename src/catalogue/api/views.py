# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import json
import os.path
from urllib.request import urlopen
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django_filters import rest_framework as dfilters
from rest_framework import filters
from rest_framework.generics import (ListAPIView, RetrieveAPIView,
                                     RetrieveUpdateAPIView, get_object_or_404)
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework import status
from api.handlers import read_tags
from api.utils import vary_on_auth
from catalogue.forms import BookImportForm
from catalogue.helpers import get_top_level_related_tags
from catalogue.models import Book, Collection, Tag, Fragment, BookMedia
from catalogue.models.tag import prefetch_relations
from club.models import Membership
from club.permissions import IsClubMember
from sortify import sortify
from wolnelektury.utils import re_escape
from .helpers import books_after, order_books
from . import serializers


book_tag_categories = ['author', 'epoch', 'kind', 'genre']


class LegacyListAPIView(ListAPIView):
    pagination_class = None


class CreateOnPutMixin:
    '''
    Creates a new model instance when PUTting a nonexistent resource.
    '''
    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            if self.request.method == 'PUT':
                lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
                return self.get_queryset().model(**{
                    self.lookup_field: self.kwargs[lookup_url_kwarg]
                })
            else:
                raise


class CollectionList(LegacyListAPIView):
    queryset = Collection.objects.filter(listed=True)
    serializer_class = serializers.CollectionListSerializer


@vary_on_auth  # Because of 'liked'.
class CollectionDetail(CreateOnPutMixin, RetrieveUpdateAPIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = Collection.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.CollectionSerializer


@vary_on_auth  # Because of 'liked'.
class BookList(LegacyListAPIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = Book.objects.none()  # Required for DjangoModelPermissions
    serializer_class = serializers.BookListSerializer

    def get(self, request, filename=None, **kwargs):
        if filename and not kwargs.get('tags') and 'count' not in request.query_params:
            try:
                with open(os.path.join(settings.MEDIA_ROOT, 'api', '%s.%s' % (filename, request.accepted_renderer.format)), 'rb') as f:
                    content = f.read()
                return HttpResponse(content, content_type=request.accepted_media_type)
            except:
                pass
        return super().get(request, filename=filename, **kwargs)

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
        if count:
            try:
                count = int(count)
            except TypeError:
                raise Http404  # Fixme

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
        books = books.filter(findable=True)
        books = order_books(books, new_api)

        if not Membership.is_active_for(self.request.user):
            books = books.exclude(preview=True)

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
        if kwargs.get('audiobooks'):
            return self.post_audiobook(request, **kwargs)
        else:
            return self.post_book(request, **kwargs)

    def post_book(self, request, **kwargs):
        data = json.loads(request.POST.get('data'))
        form = BookImportForm(data)
        if form.is_valid():
            form.save()
            return Response({}, status=status.HTTP_201_CREATED)
        else:
            raise Http404

    def post_audiobook(self, request, **kwargs):
        index = int(request.POST['part_index'])
        parts_count = int(request.POST['parts_count'])
        media_type = request.POST['type'].lower()
        source_sha1 = request.POST.get('source_sha1')
        name = request.POST.get('name', '')
        part_name = request.POST.get('part_name', '')

        project_description = request.POST.get('project_description', '')
        project_icon = request.POST.get('project_icon', '')

        _rest, slug = request.POST['book'].rstrip('/').rsplit('/', 1)
        book = Book.objects.get(slug=slug)

        try:
            assert source_sha1
            bm = book.media.get(type=media_type, source_sha1=source_sha1)
        except (AssertionError, BookMedia.DoesNotExist):
            bm = BookMedia(book=book, type=media_type)
        bm.name = name
        bm.part_name = part_name
        bm.index = index
        bm.project_description = project_description
        bm.project_icon = project_icon
        bm.file.save(None, request.data['file'], save=False)
        bm.save(parts_count=parts_count)

        return Response({}, status=status.HTTP_201_CREATED)


class BookFilter(dfilters.FilterSet):
    sort = dfilters.OrderingFilter(
        fields=(
            ('sort_key_author', 'alpha'),
            ('popularity', 'popularity'),
        )
    )
    tag = dfilters.ModelMultipleChoiceFilter(
        field_name='tag_relations__tag',
        queryset=Tag.objects.filter(category__in=('author', 'epoch', 'genre', 'kind')),
        conjoined=True,
    )


class BookList2(ListAPIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = Book.objects.none()  # Required for DjangoModelPermissions
    serializer_class = serializers.BookSerializer2
    filter_backends = (
        dfilters.DjangoFilterBackend,
        filters.SearchFilter,
    )
    filterset_class = BookFilter
    search_fields = [
        'title',
    ]

    def get_queryset(self):
        books = Book.objects.all()
        books = books.filter(findable=True)
        books = order_books(books, True)

        return books


class BookList11Labs(BookList2):
    serializer_class = serializers.BookSerializer11Labs

    def get_queryset(self):
        books = Book.objects.all()
        books = books.filter(findable=True)
        books = books.filter(license='')
        books = order_books(books, True)

        return books


@vary_on_auth  # Because of 'liked'.
class BookDetail(RetrieveAPIView):
    queryset = Book.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.BookDetailSerializer


class BookDetail2(RetrieveAPIView):
    queryset = Book.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.BookSerializer2


@vary_on_auth  # Because of embargo links.
class EbookList(BookList):
    serializer_class = serializers.EbookSerializer


@method_decorator(never_cache, name='dispatch')
class Preview(LegacyListAPIView):
    #queryset = Book.objects.filter(preview=True)
    serializer_class = serializers.BookPreviewSerializer

    def get_queryset(self):
        qs = Book.objects.filter(preview=True)
        # FIXME: temporary workaround for a problem with iOS app; see #3954.
        if 'Darwin' in self.request.META.get('HTTP_USER_AGENT', '') and 'debug' not in self.request.GET:
            qs = qs.none()
        return qs


@vary_on_auth  # Because of 'liked'.
class FilterBookList(LegacyListAPIView):
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
        if not Membership.is_active_for(self.request.user):
            preview = False

        new_api = self.request.query_params.get('new_api')
        after = self.request.query_params.get('after')
        count = int(self.request.query_params.get('count', 50))
        books = order_books(Book.objects.distinct(), new_api)
        books = books.filter(findable=True)
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
    permission_classes = [IsClubMember]

    @method_decorator(never_cache)
    def get(self, *args, **kwargs):
        return HttpResponse(self.get_object().get_media('epub'))


class TagCategoryView(LegacyListAPIView):
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        category = self.kwargs['category']
        tags = Tag.objects.filter(category=category).exclude(items=None).order_by('slug')

        after = self.request.query_params.get('after')
        count = self.request.query_params.get('count')
        if after:
            tags = tags.filter(slug__gt=after)
        if count:
            tags = tags[:count]

        return tags

class AuthorList(ListAPIView):
    serializer_class = serializers.AuthorSerializer
    queryset = Tag.objects.filter(category='author')

class AuthorView(RetrieveAPIView):
    serializer_class = serializers.AuthorSerializer
    queryset = Tag.objects.filter(category='author')
    lookup_field = 'slug'

class EpochList(ListAPIView):
    serializer_class = serializers.EpochSerializer
    queryset = Tag.objects.filter(category='epoch')

class EpochView(RetrieveAPIView):
    serializer_class = serializers.EpochSerializer
    queryset = Tag.objects.filter(category='epoch')
    lookup_field = 'slug'

class GenreList(ListAPIView):
    serializer_class = serializers.GenreSerializer
    queryset = Tag.objects.filter(category='genre')

class GenreView(RetrieveAPIView):
    serializer_class = serializers.GenreSerializer
    queryset = Tag.objects.filter(category='genre')
    lookup_field = 'slug'

class KindList(ListAPIView):
    serializer_class = serializers.KindSerializer
    queryset = Tag.objects.filter(category='kind')

class KindView(RetrieveAPIView):
    serializer_class = serializers.KindSerializer
    queryset = Tag.objects.filter(category='kind')
    lookup_field = 'slug'


class TagView(RetrieveAPIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = serializers.TagDetailSerializer
    queryset = Tag.objects.all()
    
    def get_object(self):
        try:
            return get_object_or_404(
                Tag,
                category=self.kwargs['category'],
                slug=self.kwargs['slug']
            )
        except Http404:
            if self.request.method == 'POST':
                return Tag(
                    category=self.kwargs['category'],
                    slug=self.kwargs['slug']
                )
            else:
                raise

    def post(self, request, **kwargs):
        data = json.loads(request.POST.get('data'))
        fields = {
            "name_pl": "name_pl",
            "description_pl": "description_pl",
            "plural": "plural",
            "is_epoch_specific": "genre_epoch_specific",
            "collective_noun": "collective_noun",
            "adjective_feminine_singular": "adjective_feminine_singular",
            "adjective_nonmasculine_plural": "adjective_nonmasculine_plural",
            "genitive": "genitive",
            "collective_noun": "collective_noun",
            "gazeta_link": "gazeta_link",
            "culturepl_link": "culturepl_link",
            "wiki_link_pl": "wiki_link_pl",
            "photo_attribution": "photo_attribution",
        }
        obj = self.get_object()
        updated = set()
        for data_field, model_field in fields.items():
            value = data.get(data_field)
            if value:
                if obj.category == 'author' and model_field == 'name_pl':
                    obj.sort_key = sortify(value.lower())
                    updated.add('sort_key')
                    value = ' '.join(reversed([t.strip() for t in value.split(',', 1)]))
                setattr(obj, model_field, value)
                updated.add(model_field)
        if data.get('photo'):
            response = urlopen(data['photo'])
            ext = response.headers.get('Content-Type', '').rsplit('/', 1)[-1]
            obj.photo.save(
                "{}.{}".format(self.kwargs['slug'], ext),
                ContentFile(response.read()),
                save=False,
            )
            updated.add('photo')

        if obj.pk:
            obj.save(update_fields=updated, quick=True)
        else:
            obj.save()
        return Response({})


@vary_on_auth  # Because of 'liked'.
class FragmentList(LegacyListAPIView):
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
        return Fragment.tagged.with_all(tags).filter(book__findable=True).select_related('book')


@vary_on_auth  # Because of 'liked'.
class FragmentView(RetrieveAPIView):
    serializer_class = serializers.FragmentDetailSerializer

    def get_object(self):
        return get_object_or_404(
            Fragment,
            book__slug=self.kwargs['book'],
            anchor=self.kwargs['anchor']
        )


class SuggestedTags(ListAPIView):
    serializer_class = serializers.FilterTagSerializer

    def get_queryset(self):
        tag_ids = self.request.GET.getlist('tag', [])
        tags = [get_object_or_404(Tag, id=tid) for tid in tag_ids]
        related_tags = list(t.id for t in get_top_level_related_tags(tags))
        return Tag.objects.filter(id__in=related_tags)
