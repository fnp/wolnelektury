from django.http import HttpResponse
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from paypal.permissions import IsSubscribed
from api.handlers import read_tags
from . import serializers
from catalogue.models import Book, Collection, Tag, Fragment


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


class EpubView(RetrieveAPIView):
    queryset = Book.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsSubscribed]

    def get(self, *args, **kwargs):
        return HttpResponse(self.get_object().get_media('epub'))


class TagCategoryView(ListAPIView):
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        category = self.kwargs['category']
        tags = Tag.objects.filter(category=category).exclude(items=None).order_by('slug')
        if self.request.query_params.get('book_only') == 'true':
            tags = tags.filter(for_books=True)
        if self.request.GET.get('picture_only') == 'true':
            tags = filter(for_pictures=True)

        after = self.request.query_params.get('after')
        count = self.request.query_params.get('count')
        if after:
            tags = tags.filter(slug__gt=after)
        if count:
            tags = tags[:count]

        return tags


class TagView(RetrieveAPIView):
    serializer_class = serializers.TagDetailSerializer

    def get_object(self):
        return get_object_or_404(
            Tag,
            category=self.kwargs['category'],
            slug=self.kwargs['slug']
        )


class FragmentList(ListAPIView):
    serializer_class = serializers.FragmentSerializer

    def get_queryset(self):
        try:
            tags, ancestors = read_tags(
                self.kwargs['tags'],
                self.request,
                allowed={'author', 'epoch', 'kind', 'genre', 'book', 'theme'}
            )
        except ValueError:
            raise Http404
        return Fragment.tagged.with_all(tags).select_related('book')


class FragmentView(RetrieveAPIView):
    serializer_class = serializers.FragmentDetailSerializer

    def get_object(self):
        return get_object_or_404(
            Fragment,
            book__slug=self.kwargs['book'],
            anchor=self.kwargs['anchor']
        )
