from django.http import Http404, HttpResponse
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework import status
from paypal.permissions import IsSubscribed
from api.handlers import read_tags
from .helpers import books_after, order_books
from . import serializers
from catalogue.models import Book, Collection, Tag, Fragment
from catalogue.models.tag import prefetch_relations


class CollectionList(ListAPIView):
    queryset = Collection.objects.all()
    serializer_class = serializers.CollectionListSerializer


class CollectionDetail(RetrieveAPIView):
    queryset = Collection.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.CollectionSerializer


class BookList(ListAPIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = Book.objects.none()  # Required for DjangoModelPermissions
    serializer_class = serializers.BaseBookSerializer

    def get_queryset(self):
        try:
            tags, ancestors = read_tags(
                self.kwargs['tags'], self.request,
                allowed=('author', 'epoch', 'kind', 'genre')
            )
        except ValueError:
            raise Http404

        new_api = self.request.query_params.get('new_api')
        after = self.request.query_params.get('after', self.kwargs.get('after'))
        count = self.request.query_params.get('count', self.kwargs.get('count'))

        if tags:
            if self.kwargs.get('top_level'):
                books = Book.tagged_top_level(tags)
                if not books:
                    raise Http404
                return books
            else:
                books = Book.tagged.with_all(tags)
        else:
            books = Book.objects.all()
        books = order_books(books, new_api)

        if self.kwargs.get('top_level'):
            books = books.filter(parent=None)
        if self.kwargs.get('audiobooks'):
            books = books.filter(media__type='mp3').distinct()
        if self.kwargs.get('daisy'):
            books = books.filter(media__type='daisy').distinct()
        if self.kwargs.get('recommended'):
            books = books.filter(recommended=True)
        if self.kwargs.get('newest'):
            books = books.order_by('-created_at')

        if after:
            books = books_after(books, after, new_api)

        prefetch_relations(books, 'author')
        prefetch_relations(books, 'genre')
        prefetch_relations(books, 'kind')
        prefetch_relations(books, 'epoch')

        if count:
            books = books[:count]

        return books

    def post(self, request):
        # Permission needed.
        data = json.loads(request.POST.get('data'))
        form = BookImportForm(data)
        if form.is_valid():
            form.save()
            return Response({}, status=status.HTTP_201_CREATED)
        else:
            raise Http404


class BookDetail(RetrieveAPIView):
    queryset = Book.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.BookDetailSerializer


class Preview(ListAPIView):
    queryset = Book.objects.filter(preview=True)
    serializer_class = serializers.BookPreviewSerializer


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
