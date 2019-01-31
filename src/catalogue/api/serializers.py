from rest_framework import serializers
from api.fields import AbsoluteURLField, LegacyMixin
from catalogue.models import Book, Collection, Tag, BookMedia
from .fields import BookLiked, ThumbnailField


class TagSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField()
    href = AbsoluteURLField(
        view_name='api_tag',
        view_args=('category:category_plural', 'slug')
    )

    class Meta:
        model = Tag
        fields = ['url', 'href', 'name', 'slug']


class BookSerializer(LegacyMixin, serializers.ModelSerializer):
    author = serializers.CharField(source='author_unicode')
    kind = serializers.CharField(source='kind_unicode')
    epoch = serializers.CharField(source='epoch_unicode')
    genre = serializers.CharField(source='genre_unicode')

    simple_thumb = serializers.FileField(source='cover_api_thumb')
    href = AbsoluteURLField(view_name='catalogue_api_book', view_args=['slug'])
    url = AbsoluteURLField()
    liked = BookLiked()
    cover_thumb = ThumbnailField('139x193', source='cover')

    class Meta:
        model = Book
        fields = [
            'kind', 'full_sort_key', 'title', 'url', 'cover_color', 'author',
            'cover', 'liked', 'epoch', 'href', 'has_audio', 'genre',
            'simple_thumb', 'slug', 'cover_thumb']
        legacy_non_null_fields = [
            'kind', 'author', 'epoch', 'genre',
            'cover', 'simple_thumb', 'cover_thumb']


class MediaSerializer(LegacyMixin, serializers.ModelSerializer):
    url = serializers.FileField(source='file')

    class Meta:
        model = BookMedia
        fields = ['url', 'director', 'type', 'name', 'artist']
        legacy_non_null_fields = ['director', 'artist']


class BookDetailSerializer(LegacyMixin, serializers.ModelSerializer):
    url = AbsoluteURLField()

    authors = TagSerializer(many=True)
    epochs = TagSerializer(many=True)
    genres = TagSerializer(many=True)
    kinds = TagSerializer(many=True)

    fragment_data = serializers.DictField()
    parent = BookSerializer()
    children = BookSerializer(many=True)

    xml = AbsoluteURLField(source='xml_url')
    html = AbsoluteURLField(source='html_url')
    txt = AbsoluteURLField(source='txt_url')
    fb2 = AbsoluteURLField(source='fb2_url')
    epub = AbsoluteURLField(source='epub_url')
    mobi = AbsoluteURLField(source='mobi_url')
    pdf = AbsoluteURLField(source='pdf_url')
    media = MediaSerializer(many=True)
    cover_thumb = ThumbnailField('139x193', source='cover')
    simple_thumb = serializers.FileField(source='cover_api_thumb')

    class Meta:
        model = Book
        fields = [
            'title', 'url',
            'epochs', 'genres', 'kinds', 'authors',
            'fragment_data', 'children', 'parent', 'preview',
            'epub', 'mobi', 'pdf', 'html', 'txt', 'fb2', 'xml', 'media', 'audio_length',
            'cover_color', 'simple_cover', 'cover_thumb', 'cover', 'simple_thumb'
        ]
        legacy_non_null_fields = ['html', 'txt', 'fb2', 'epub', 'mobi', 'pdf',
                                  'cover', 'simple_cover', 'cover_thumb', 'simple_thumb']


class CollectionListSerializer(serializers.ModelSerializer):
    url = AbsoluteURLField()
    href = AbsoluteURLField(view_name='collection-detail', view_args=['slug'])

    class Meta:
        model = Collection
        fields = ['url', 'href', 'title']


class CollectionSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, source='get_books')
    url = AbsoluteURLField()

    class Meta:
        model = Collection
        fields = ['url', 'books', 'description', 'title']
