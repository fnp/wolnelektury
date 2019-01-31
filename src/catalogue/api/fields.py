from rest_framework import serializers
from sorl.thumbnail import default
from catalogue.models import Book


class BookLiked(serializers.ReadOnlyField):
    def __init__(self, source='pk', **kwargs):
        super(BookLiked, self).__init__(source=source, **kwargs)

    def to_representation(self, value):
        request = self.context['request']
        if not hasattr(request, 'liked_books'):
            if request.user.is_authenticated():
                request.liked_books = set(Book.tagged.with_any(request.user.tag_set.all()).values_list('id', flat=True))
            else:
                request.liked_books = None
        if request.liked_books is not None:
            return value in request.liked_books


class ThumbnailField(serializers.FileField):
    def __init__(self, geometry, *args, **kwargs):
        self.geometry = geometry
        super(ThumbnailField, self).__init__(*args, **kwargs)
        
    def to_representation(self, value):
        if value:
            return super(ThumbnailField, self).to_representation(
                default.backend.get_thumbnail(value, self.geometry)
            )
