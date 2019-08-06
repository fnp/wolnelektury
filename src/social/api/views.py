# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.http import Http404
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import BookUserData
from api.utils import vary_on_auth
from catalogue.api.helpers import order_books, books_after
from catalogue.api.serializers import BookSerializer
from catalogue.models import Book
from social.utils import likes


@vary_on_auth
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


@vary_on_auth
class ShelfView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer

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

