# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from rest_framework import serializers
from api.fields import AbsoluteURLField, LegacyMixin, ThumbnailField
from catalogue.models import Book, Collection, Tag, BookMedia, Fragment
from .fields import BookLiked, EmbargoURLField


class TagSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField()
    href = AbsoluteURLField(
        view_name='catalogue_api_tag',
        view_args=('category', 'slug')
    )

    class Meta:
        model = Tag
        fields = ['url', 'href', 'name', 'slug']


class TagDetailSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField()

    class Meta:
        model = Tag
        fields = [
            'name', 'url', 'sort_key',
            'description',
            'description_pl',
            'plural', 'genre_epoch_specific',
            'adjective_feminine_singular', 'adjective_nonmasculine_plural',
            'genitive', 'collective_noun',
        ]
        write_only_fields = [
            'description_pl',
            'plural', 'genre_epoch_specific',
            'adjective_feminine_singular', 'adjective_nonmasculine_plural',
            'genitive', 'collective_noun',
        ]


class AuthorItemSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField()
    href = AbsoluteURLField(
        view_name='catalogue_api_author',
        view_args=('slug',)
    )

    class Meta:
        model = Tag
        fields = [
            'url', 'href', 'name'
        ]

class AuthorSerializer(AuthorItemSerializer):
    photo_thumb = ThumbnailField('139x193', source='photo')

    class Meta:
        model = Tag
        fields = [
            'url', 'href', 'name', 'slug', 'sort_key', 'description',
            'genitive', 'photo', 'photo_thumb', 'photo_attribution',
        ]

class EpochItemSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField()
    href = AbsoluteURLField(
        view_name='catalogue_api_epoch',
        view_args=('slug',)
    )
    class Meta:
        model = Tag
        fields = ['url', 'href', 'name']

class EpochSerializer(EpochItemSerializer):
    class Meta:
        model = Tag
        fields = [
            'url', 'href', 'name', 'slug', 'sort_key', 'description',
            'adjective_feminine_singular', 'adjective_nonmasculine_plural',
        ]

class GenreItemSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField()
    href = AbsoluteURLField(
        view_name='catalogue_api_genre',
        view_args=('slug',)
    )
    class Meta:
        model = Tag
        fields = ['url', 'href', 'name']

class GenreSerializer(GenreItemSerializer):
    class Meta:
        model = Tag
        fields = [
            'url', 'href', 'name', 'slug', 'sort_key', 'description',
            'plural', 'genre_epoch_specific',
        ]

class KindItemSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField()
    href = AbsoluteURLField(
        view_name='catalogue_api_kind',
        view_args=('slug',)
    )
    class Meta:
        model = Tag
        fields = ['url', 'href', 'name']

class KindSerializer(KindItemSerializer):
    class Meta:
        model = Tag
        fields = [
            'url', 'href', 'name', 'slug', 'sort_key', 'description',
            'collective_noun',
        ]


class TranslatorSerializer(serializers.Serializer):
    name = serializers.CharField(source='*')


class BookSerializer2(serializers.ModelSerializer):
    url = AbsoluteURLField()
    href = AbsoluteURLField(view_name='catalogue_api_book', view_args=['slug'])
    xml = EmbargoURLField(source='xml_url')
    html = EmbargoURLField(source='html_url')
    txt = EmbargoURLField(source='txt_url')
    fb2 = EmbargoURLField(source='fb2_url')
    epub = EmbargoURLField(source='epub_url')
    mobi = EmbargoURLField(source='mobi_url')
    pdf = EmbargoURLField(source='pdf_url')

    authors = AuthorItemSerializer(many=True)
    translators = AuthorItemSerializer(many=True)
    epochs = EpochItemSerializer(many=True)
    genres = GenreItemSerializer(many=True)
    kinds = KindItemSerializer(many=True)
    parent = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='catalogue_api_book',
        lookup_field='slug'
    )

    class Meta:
        model = Book
        fields = [
            'slug', 'title', 'full_sort_key',
            'href', 'url', 'language',
            'authors', 'translators',
            'epochs', 'genres', 'kinds',
            #'children',
            'parent', 'preview',
            'epub', 'mobi', 'pdf', 'html', 'txt', 'fb2', 'xml',
            'cover_thumb', 'cover',
            'isbn_pdf', 'isbn_epub', 'isbn_mobi',
        ]

class BookSerializer11Labs(serializers.ModelSerializer):
    url = AbsoluteURLField()
    href = AbsoluteURLField(view_name='catalogue_api_book', view_args=['slug'])
    html = EmbargoURLField(source='html_nonotes_url')

    authors = AuthorItemSerializer(many=True)
    translators = AuthorItemSerializer(many=True)
    epochs = EpochItemSerializer(many=True)
    genres = GenreItemSerializer(many=True)
    kinds = KindItemSerializer(many=True)
    parent = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='catalogue_api_book',
        lookup_field='slug'
    )

    class Meta:
        model = Book
        fields = [
            'slug', 'title', 'full_sort_key',
            'href', 'url', 'language',
            'authors', 'translators',
            'epochs', 'genres', 'kinds',
            #'children',
            'parent', 'preview',
            'html',
            'cover_thumb', 'cover',
            'isbn_pdf', 'isbn_epub', 'isbn_mobi',
        ]


class BookSerializer(LegacyMixin, serializers.ModelSerializer):
    author = serializers.CharField(source='author_unicode')
    kind = serializers.CharField(source='kind_unicode')
    epoch = serializers.CharField(source='epoch_unicode')
    genre = serializers.CharField(source='genre_unicode')
    liked = BookLiked()

    simple_thumb = serializers.FileField(source='cover_api_thumb')
    href = AbsoluteURLField(view_name='catalogue_api_book', view_args=['slug'])
    url = AbsoluteURLField()
    cover_thumb = ThumbnailField('139x193', source='cover')

    class Meta:
        model = Book
        fields = [
            'kind', 'full_sort_key', 'title', 'url', 'cover_color', 'author',
            'cover', 'epoch', 'href', 'has_audio', 'genre',
            'simple_thumb', 'slug', 'cover_thumb', 'liked']
        legacy_non_null_fields = [
            'kind', 'author', 'epoch', 'genre',
            'cover', 'simple_thumb', 'cover_thumb']


class BookListSerializer(BookSerializer):
    cover = serializers.CharField()
    cover_thumb = serializers.CharField()

    Meta = BookSerializer.Meta


class FilterBookListSerializer(BookListSerializer):
    key = serializers.CharField()

    class Meta:
        model = Book
        fields = BookListSerializer.Meta.fields + ['key']
        legacy_non_null_fields = BookListSerializer.Meta.legacy_non_null_fields


class MediaSerializer(LegacyMixin, serializers.ModelSerializer):
    url = EmbargoURLField(source='file_url')

    class Meta:
        model = BookMedia
        fields = ['url', 'director', 'type', 'name', 'artist']
        legacy_non_null_fields = ['director', 'artist']


class BookDetailSerializer(LegacyMixin, serializers.ModelSerializer):
    url = AbsoluteURLField()

    authors = TagSerializer(many=True)
    translators = TranslatorSerializer(many=True)
    epochs = TagSerializer(many=True)
    genres = TagSerializer(many=True)
    kinds = TagSerializer(many=True)

    fragment_data = serializers.DictField()
    parent = BookSerializer()
    children = BookSerializer(many=True)

    xml = EmbargoURLField(source='xml_url')
    html = EmbargoURLField(source='html_url')
    txt = EmbargoURLField(source='txt_url')
    fb2 = EmbargoURLField(source='fb2_url')
    epub = EmbargoURLField(source='epub_url')
    mobi = EmbargoURLField(source='mobi_url')
    pdf = EmbargoURLField(source='pdf_url')
    media = MediaSerializer(many=True)
    cover_thumb = ThumbnailField('139x193', source='cover')
    simple_thumb = serializers.FileField(source='cover_api_thumb')

    class Meta:
        model = Book
        fields = [
            'title', 'url', 'language',
            'epochs', 'genres', 'kinds', 'authors', 'translators',
            'fragment_data', 'children', 'parent', 'preview',
            'epub', 'mobi', 'pdf', 'html', 'txt', 'fb2', 'xml', 'media', 'audio_length',
            'cover_color', 'simple_cover', 'cover_thumb', 'cover', 'simple_thumb',
            'isbn_pdf', 'isbn_epub', 'isbn_mobi',
        ]
        legacy_non_null_fields = ['html', 'txt', 'fb2', 'epub', 'mobi', 'pdf',
                                  'cover', 'simple_cover', 'cover_thumb', 'simple_thumb']


class BookPreviewSerializer(BookDetailSerializer):
    class Meta:
        model = Book
        fields = BookDetailSerializer.Meta.fields + ['slug']
        legacy_non_null_fields = BookDetailSerializer.Meta.legacy_non_null_fields


class EbookSerializer(BookListSerializer):
    txt = EmbargoURLField(source='txt_url')
    fb2 = EmbargoURLField(source='fb2_url')
    epub = EmbargoURLField(source='epub_url')
    mobi = EmbargoURLField(source='mobi_url')
    pdf = EmbargoURLField(source='pdf_url')

    class Meta:
        model = Book
        fields = ['author', 'href', 'title', 'cover', 'slug'] + Book.ebook_formats
        legacy_non_null_fields = ['author', 'cover'] + Book.ebook_formats


class CollectionListSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField()
    href = AbsoluteURLField(view_name='collection-detail', view_args=['slug'])

    class Meta:
        model = Collection
        fields = ['url', 'href', 'title']


class CollectionSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, source='get_books', read_only=True)
    authors = TagSerializer(many=True, read_only=True)
    book_slugs = serializers.CharField(write_only=True, required=False)
    author_slugs = serializers.CharField(write_only=True, required=False)
    url = AbsoluteURLField()

    class Meta:
        model = Collection
        fields = [
            'url', 'books', 'description', 'title',
            'book_slugs', 'authors', 'author_slugs'
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        author_slugs = validated_data.get('author_slugs', '').strip().split()
        if author_slugs:
            authors = Tag.objects.filter(
                category='author',
                slug__in=author_slugs
            )
        else:
            authors = []
        instance.authors.set(authors)
        return instance


class FragmentSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    url = AbsoluteURLField()
    href = AbsoluteURLField(source='get_api_url')

    class Meta:
        model = Fragment
        fields = ['book', 'url', 'anchor', 'href']


class FragmentDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    url = AbsoluteURLField()
    themes = TagSerializer(many=True)

    class Meta:
        model = Fragment
        fields = ['book', 'anchor', 'text', 'url', 'themes']


class FragmentSerializer2(serializers.ModelSerializer):
    url = AbsoluteURLField()
    html = serializers.CharField(source='text')

    class Meta:
        model = Fragment
        fields = ['anchor', 'html', 'url']


class FilterTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'category', 'name']
