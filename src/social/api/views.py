# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from datetime import datetime
from pytz import utc
from django.http import Http404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from api.models import BookUserData
from api.utils import vary_on_auth, never_cache
from catalogue.api.helpers import order_books, books_after
from catalogue.api.serializers import BookSerializer
from catalogue.models import Book
import catalogue.models
from social.utils import likes, get_set
from social.views import get_sets_for_book_ids
from social import models


@never_cache
class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        return Response({"likes": likes(request.user, book)})

    def post(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        action = request.query_params.get('action', 'like')
        if action == 'like':
            book.like(request.user)
        elif action == 'unlike':
            book.unlike(request.user)
        return Response({})


@never_cache
class LikeView2(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        return Response({"likes": likes(request.user, book)})

    def put(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        book.like(request.user)
        return Response({"likes": likes(request.user, book)})

    def delete(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        book.unlike(request.user)
        return Response({"likes": likes(request.user, book)})


@never_cache
class LikesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        slugs = request.GET.getlist('slug')
        books = Book.objects.filter(slug__in=slugs)
        books = {b.id: b.slug for b in books}
        ids = books.keys()
        res = get_sets_for_book_ids(ids, request.user)
        res = {books[bid]: v for bid, v in res.items()}

        return Response(res)


@never_cache
class MyLikesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ids = catalogue.models.tag.TagRelation.objects.filter(tag__user=request.user).values_list('object_id', flat=True).distinct()
        books = Book.objects.filter(id__in=ids)
        books = {b.id: b.slug for b in books}
        res = get_sets_for_book_ids(ids, request.user)
        res = {books[bid]: v for bid, v in res.items()}

        res = list(books.values())
        res.sort()
        return Response(res)


class TaggedBooksField(serializers.Field):
    def to_representation(self, value):
        return catalogue.models.Book.tagged.with_all([value]).values_list('slug', flat=True)

    def to_internal_value(self, value):
        return {'books': catalogue.models.Book.objects.filter(slug__in=value)}


class UserListSerializer(serializers.ModelSerializer):
    books = TaggedBooksField(source='*')

    class Meta:
        model = catalogue.models.Tag
        fields = ['name', 'slug', 'books']
        read_only_fields = ['slug']

    def create(self, validated_data):
        instance = get_set(validated_data['user'], validated_data['name'])
        catalogue.models.tag.TagRelation.objects.filter(tag=instance).delete()
        for book in validated_data['books']:
            catalogue.models.Tag.objects.add_tag(book, instance)
        return instance

    def update(self, instance, validated_data):
        catalogue.models.tag.TagRelation.objects.filter(tag=instance).delete()
        for book in validated_data['books']:
            catalogue.models.Tag.objects.add_tag(book, instance)
        return instance

class UserListBooksSerializer(UserListSerializer):
    class Meta:
        model = catalogue.models.Tag
        fields = ['books']


@never_cache
class ListsView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    #pagination_class = None
    serializer_class = UserListSerializer

    def get_queryset(self):
        return catalogue.models.Tag.objects.filter(user=self.request.user).exclude(name='')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@never_cache
class ListView(RetrieveUpdateDestroyAPIView):
    # TODO: check if can modify
    permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer

    def get_object(self):
        return get_object_or_404(catalogue.models.Tag, slug=self.kwargs['slug'], user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, slug):
        serializer = UserListBooksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        for book in serializer.validated_data['books']:
            catalogue.models.Tag.objects.add_tag(book, instance)
        return Response(self.get_serializer(instance).data)


@never_cache
class ListItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, slug, book):
        instance = get_object_or_404(catalogue.models.Tag, slug=slug, user=self.request.user)
        book = get_object_or_404(catalogue.models.Book, slug=book)
        catalogue.models.Tag.objects.remove_tag(book, instance)
        return Response(UserListSerializer(instance).data)


@vary_on_auth
class ShelfView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer
    pagination_class = None

    def get_queryset(self):
        state = self.kwargs['state']
        if state not in ('reading', 'complete', 'likes'):
            raise Http404
        new_api = self.request.query_params.get('new_api')
        after = self.request.query_params.get('after')
        count = int(self.request.query_params.get('count', 50))
        if state == 'likes':
            books = Book.tagged.with_any(self.request.user.tag_set.all())
        else:
            ids = BookUserData.objects.filter(user=self.request.user, complete=state == 'complete')\
                .values_list('book_id', flat=True)
            books = Book.objects.filter(id__in=list(ids)).distinct()
            books = order_books(books, new_api)
        if after:
            books = books_after(books, after, new_api)
        if count:
            books = books[:count]

        return books



class ProgressSerializer(serializers.ModelSerializer):
    book = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='catalogue_api_book',
        lookup_field='slug'
    )
    book_slug = serializers.SlugRelatedField(source='book', read_only=True, slug_field='slug')

    class Meta:
        model = models.Progress
        fields = ['book', 'book_slug', 'last_mode', 'text_percent',
    'text_anchor',
    'audio_percent',
    'audio_timestamp',
    'implicit_text_percent',
    'implicit_text_anchor',
    'implicit_audio_percent',
    'implicit_audio_timestamp',
    ]


class TextProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Progress
        fields = [
                'text_percent',
                'text_anchor',
                ]
        read_only_fields = ['text_percent']

class AudioProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Progress
        fields = ['audio_percent', 'audio_timestamp']
        read_only_fields = ['audio_percent']


@never_cache
class ProgressListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgressSerializer

    def get_queryset(self):
        return models.Progress.objects.filter(user=self.request.user).order_by('-updated_at')


class ProgressMixin:
    def get_object(self):
        try:
            return models.Progress.objects.get(user=self.request.user, book__slug=self.kwargs['slug'])
        except models.Progress.DoesNotExist:
            book = get_object_or_404(Book, slug=self.kwargs['slug'])
            return models.Progress(user=self.request.user, book=book)



@never_cache
class ProgressView(ProgressMixin, RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgressSerializer


@never_cache
class TextProgressView(ProgressMixin, RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TextProgressSerializer

    def perform_update(self, serializer):
        serializer.instance.last_mode = 'text'
        serializer.save()


@never_cache
class AudioProgressView(ProgressMixin, RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AudioProgressSerializer

    def perform_update(self, serializer):
        serializer.instance.last_mode = 'audio'
        serializer.save()



class SyncSerializer(serializers.Serializer):
    timestamp = serializers.IntegerField()
    type = serializers.CharField()
    id = serializers.CharField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['object'] = instance['object'].data
        return rep

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        ret['object'] = data['object']
        return ret


class SyncView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SyncSerializer

    def get_queryset(self):
        try:
            timestamp = int(self.request.GET.get('ts'))
        except:
            timestamp = 0

        timestamp = datetime.fromtimestamp(timestamp, tz=utc)
        
        data = []
        for p in models.Progress.objects.filter(
                user=self.request.user,
                updated_at__gt=timestamp).order_by('updated_at'):
            data.append({
                'timestamp': p.updated_at.timestamp(),
                'type': 'progress',
                'id': p.book.slug,
                'object': ProgressSerializer(
                    p, context={'request': self.request}
                ) if not p.deleted else None
            })
        return data

    def post(self, request):
        data = request.data
        for item in data:
            ser = SyncSerializer(data=item)
            ser.is_valid(raise_exception=True)
            d = ser.validated_data
            if d['type'] == 'progress':
                models.Progress.sync(
                    user=request.user,
                    slug=d['id'],
                    ts=datetime.fromtimestamp(d['timestamp'], tz=utc),
                    data=d['object']
                )
        return Response()
