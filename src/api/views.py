# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from migdal.models import Entry
from catalogue.models import Book
from .models import BookUserData
from . import serializers


class UserView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user


class BookUserDataView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.BookUserDataSerializer
    lookup_field = 'book__slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        return BookUserData.objects.filter(user=self.request.user)

    def get(self, *args, **kwargs):
        try:
            return super(BookUserDataView, self).get(*args, **kwargs)
        except Http404:
            return Response({"state": "not_started"})

    def post(self, request, slug, state):
        if state not in ('reading', 'complete'):
            raise Http404

        book = get_object_or_404(Book, slug=slug)
        instance = BookUserData.update(book, request.user, state)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BlogView(ListAPIView):
    serializer_class = serializers.BlogSerializer

    def get_queryset(self):
        after = self.request.query_params.get('after')
        count = int(self.request.query_params.get('count', 20))
        entries = Entry.published_objects.filter(in_stream=True).order_by('-first_published_at')
        if after:
            entries = entries.filter(first_published_at__lt=after)
        if count:
            entries = entries[:count]
        return entries
