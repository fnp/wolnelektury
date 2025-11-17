# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from datetime import datetime
from django.db.models import Q
from django.http import Http404
from django.utils.timezone import now, utc
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from api.models import BookUserData
from api.utils import vary_on_auth, never_cache
from catalogue.api.helpers import order_books, books_after
from catalogue.api.serializers import BookSerializer
from catalogue.models import Book
import catalogue.models
from social.views import get_sets_for_book_ids
from social.utils import likes
from social import models
import bookmarks.models
from bookmarks.api.views import BookmarkSerializer


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ['notifications']


class SettingsView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SettingsSerializer

    def get_object(self):
        return models.UserProfile.get_for(self.request.user)


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
            models.UserList.like(request.user, book)
        elif action == 'unlike':
            models.UserList.unlike(request.user, book)
        return Response({})


@never_cache
class LikeView2(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        return Response({"likes": likes(request.user, book)})

    def put(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        models.UserList.like(request.user, book)
        return Response({"likes": likes(request.user, book)})

    def delete(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        models.UserList.unlike(request.user, book)
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
        ul = models.UserList.get_favorites_list(request.user)
        if ul is None:
            return Response([])
        return Response(
            ul.userlistitem_set.exclude(deleted=True).exclude(book=None).values_list('book__slug', flat=True)
        )


class UserListItemsField(serializers.Field):
    def to_representation(self, value):
        return value.userlistitem_set.exclude(deleted=True).exclude(book=None).values_list('book__slug', flat=True)

    def to_internal_value(self, value):
        return {'books': catalogue.models.Book.objects.filter(slug__in=value)}


class UserListSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(write_only=True, required=False)
    books = UserListItemsField(source='*', required=False)
    timestamp = serializers.IntegerField(required=False)

    class Meta:
        model = models.UserList
        fields = [
            'timestamp',
            'client_id',
            'name',
            'slug',
            'favorites',
            'deleted',
            'books',
        ]
        read_only_fields = ['favorites']
        extra_kwargs = {
            'slug': {
                'required': False
            }
        }

    def create(self, validated_data):
        instance = models.UserList.get_by_name(
            validated_data['user'],
            validated_data['name'],
            create=True
        )
        instance.userlistitem_set.all().delete()
        for book in validated_data['books']:
            instance.append(book)
        return instance

    def update(self, instance, validated_data):
        instance.userlistitem_set.all().delete()
        for book in validated_data['books']:
            instance.append(instance)
        return instance

class UserListBooksSerializer(UserListSerializer):
    class Meta:
        model = models.UserList
        fields = ['books']


class UserListItemSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(write_only=True, required=False)
    favorites = serializers.BooleanField(required=False)
    list_slug = serializers.SlugRelatedField(
        queryset=models.UserList.objects.all(),
        source='list',
        slug_field='slug',
        required=False,
    )
    timestamp = serializers.IntegerField(required=False)
    book_slug = serializers.SlugRelatedField(
        queryset=Book.objects.all(),
        source='book',
        slug_field='slug',
        required=False
    )

    class Meta:
        model = models.UserListItem
        fields = [
            'client_id',
            'uuid',
            'order',
            'list_slug',
            'timestamp',
            'favorites',
            'deleted',

            'book_slug',
            'fragment',
            'quote',
            'bookmark',
            'note',
        ]
        extra_kwargs = {
            'order': {
                'required': False
            }
        }


@never_cache
class ListsView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    #pagination_class = None
    serializer_class = UserListSerializer

    def get_queryset(self):
        return models.UserList.objects.filter(
            user=self.request.user,
            favorites=False,
            deleted=False
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@never_cache
class ListView(RetrieveUpdateDestroyAPIView):
    # TODO: check if can modify
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = UserListSerializer

    def get_object(self):
        if self.request.method in SAFE_METHODS:
            q = Q(deleted=False)
            if self.request.user.is_authenticated:
                q |= Q(user=self.request.user)
            return get_object_or_404(
                models.UserList,
                q,
                slug=self.kwargs['slug'],
            )
        else:
            return get_object_or_404(
                models.UserList,
                slug=self.kwargs['slug'],
                user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, slug):
        serializer = UserListBooksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        for book in serializer.validated_data['books']:
            instance.append(book)
        return Response(self.get_serializer(instance).data)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.updated_at = now()
        instance.save()


@never_cache
class ListItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, slug, book):
        instance = get_object_or_404(
            models.UserList, slug=slug, user=self.request.user)
        book = get_object_or_404(catalogue.models.Book, slug=book)
        instance.remove(book=book)
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
            books = Book.objects.filter(userlistitem__list__user=self.request.user)
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
    book_slug = serializers.SlugRelatedField(
        queryset=Book.objects.all(),
        source='book',
        slug_field='slug')
    timestamp = serializers.IntegerField(required=False)

    class Meta:
        model = models.Progress
        fields = [
            'timestamp',
            'book', 'book_slug', 'last_mode', 'text_percent',
            'text_anchor',
            'audio_percent',
            'audio_timestamp',
            'implicit_text_percent',
            'implicit_text_anchor',
            'implicit_audio_percent',
            'implicit_audio_timestamp',
        ]
        extra_kwargs = {
            'last_mode': {
                'required': False,
                'default': 'text',
            }
        }


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



@never_cache
class SyncView(ListAPIView):
    permission_classes = [IsAuthenticated]
    sync_id_field = 'slug'
    sync_id_serializer_field = 'slug'
    sync_user_field = 'user'

    def get_queryset(self):
        try:
            timestamp = int(self.request.GET.get('ts'))
        except:
            timestamp = 0

        timestamp = datetime.fromtimestamp(timestamp, tz=utc)
        
        data = []
        return self.get_queryset_for_ts(timestamp)

    def get_queryset_for_ts(self, timestamp):
        return self.model.objects.filter(
            updated_at__gt=timestamp,
            **{
                self.sync_user_field: self.request.user
            }
        ).order_by('updated_at')

    def get_instance(self, user, data):
        sync_id = data.get(self.sync_id_serializer_field)
        if not sync_id:
            return None
        return self.model.objects.filter(**{
            self.sync_user_field: user,
            self.sync_id_field: sync_id
        }).first()

    def post(self, request):
        new_ids = []
        data = request.data
        if not isinstance(data, list):
            raise serializers.ValidationError('Payload should be a list')
        for item in data:
            instance = self.get_instance(request.user, item)
            ser = self.get_serializer(
                instance=instance,
                data=item
            )
            ser.is_valid(raise_exception=True)
            synced_instance = self.model.sync(
                request.user,
                instance,
                ser.validated_data
            )
            if instance is None and 'client_id' in ser.validated_data and synced_instance is not None:
                new_ids.append({
                    'client_id': ser.validated_data['client_id'],
                    self.sync_id_serializer_field: getattr(synced_instance, self.sync_id_field),
                })
        return Response(new_ids)


class ProgressSyncView(SyncView):
    model = models.Progress
    serializer_class = ProgressSerializer
    
    sync_id_field = 'book__slug'
    sync_id_serializer_field = 'book_slug'


class UserListSyncView(SyncView):
    model = models.UserList
    serializer_class = UserListSerializer


class UserListItemSyncView(SyncView):
    model = models.UserListItem
    serializer_class = UserListItemSerializer

    sync_id_field = 'uuid'
    sync_id_serializer_field = 'uuid'
    sync_user_field = 'list__user'

    def get_queryset_for_ts(self, timestamp):
        qs = self.model.objects.filter(
            updated_at__gt=timestamp,
            **{
                self.sync_user_field: self.request.user
            }
        )
        if self.request.query_params.get('favorites'):
            qs = qs.filter(list__favorites=True)
        return qs.order_by('updated_at')


class BookmarkSyncView(SyncView):
    model = bookmarks.models.Bookmark
    serializer_class = BookmarkSerializer

    sync_id_field = 'uuid'
    sync_id_serializer_field = 'uuid'

    def get_instance(self, user, data):
        ret = super().get_instance(user, data)
        if ret is None:
            if data.get('location'):
                ret = self.model.get_by_location(user, data['location'])
        return ret
