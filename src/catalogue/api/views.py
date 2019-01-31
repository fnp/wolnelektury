from rest_framework.generics import ListAPIView, RetrieveAPIView
from . import serializers
from catalogue.models import Book, Collection


class CollectionList(ListAPIView):
    queryset = Collection.objects.all()
    serializer_class = serializers.CollectionListSerializer


class CollectionDetail(RetrieveAPIView):
    queryset = Collection.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.CollectionSerializer


class BookDetail(RetrieveAPIView):
    queryset = Book.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.BookDetailSerializer
