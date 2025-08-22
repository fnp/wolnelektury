from api.utils import never_cache

from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators import cache
import catalogue.models
from wolnelektury.utils import is_ajax
from bookmarks import models
from lxml import html
import re
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from api.fields import AbsoluteURLField


class BookmarkSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(
        queryset=catalogue.models.Book.objects.all(), slug_field='slug',
        required=False
    )
    href = AbsoluteURLField(view_name='api_bookmark', view_args=['uuid'])
    timestamp = serializers.IntegerField(required=False)
    location = serializers.CharField(required=False)
    
    class Meta:
        model = models.Bookmark
        fields = ['book', 'anchor', 'audio_timestamp', 'mode', 'note', 'href', 'uuid', 'location', 'timestamp', 'deleted']
        read_only_fields = ['uuid', 'mode']



@never_cache
class BookmarksView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return self.request.user.bookmark_set.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@never_cache
class BookBookmarksView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkSerializer
    pagination_class = None

    def get_queryset(self):
        return self.request.user.bookmark_set.filter(book__slug=self.kwargs['book'])


@never_cache
class BookmarkView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.request.user.bookmark_set.all()
