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
from . import serializers
from bookmarks.api.views import BookmarkSerializer



class SettingsView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.SettingsSerializer

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


@never_cache
class ListsView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    #pagination_class = None
    serializer_class = serializers.UserListSerializer

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
    serializer_class = serializers.UserListSerializer

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
                models.UserList.all_objects.all(),
                slug=self.kwargs['slug'],
                user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, slug):
        serializer = serializers.UserListBooksSerializer(data=request.data)
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


@never_cache
class ProgressListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProgressSerializer

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
    serializer_class = serializers.ProgressSerializer


@never_cache
class TextProgressView(ProgressMixin, RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TextProgressSerializer

    def perform_update(self, serializer):
        serializer.instance.last_mode = 'text'
        serializer.save()


@never_cache
class AudioProgressView(ProgressMixin, RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AudioProgressSerializer

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
    serializer_class = serializers.ProgressSerializer
    
    sync_id_field = 'book__slug'
    sync_id_serializer_field = 'book_slug'


class UserListSyncView(SyncView):
    model = models.UserList
    serializer_class = serializers.UserListSerializer


class UserListItemSyncView(SyncView):
    model = models.UserListItem
    serializer_class = serializers.UserListItemSerializer

    sync_id_field = 'uuid'
    sync_id_serializer_field = 'uuid'
    sync_user_field = 'list__user'

    def get_queryset_for_ts(self, timestamp):
        qs = self.model.all_objects.filter(
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
