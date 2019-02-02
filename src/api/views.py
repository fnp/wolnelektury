from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, get_object_or_404
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
