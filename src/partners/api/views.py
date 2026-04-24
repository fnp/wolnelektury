from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.generics import (ListAPIView, get_object_or_404)
from rest_framework import serializers
from api.fields import AbsoluteURLField
from catalogue.models import Book
from catalogue.api.fields import EmbargoURLField
from catalogue.api.serializers import BookSerializer2
from partners import models




class PartnerBookSerializer(BookSerializer2):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'slug', 'title', 'full_sort_key',
            'href', 'url', 'language',
            'authors', 'translators',
            'epochs', 'genres', 'kinds',
            'children',
            'parent', 'preview',
            'epub', 'mobi', 'pdf', 'html', 'txt', 'fb2', 'xml',
            'cover_thumb', 'cover',
            'isbn_pdf', 'isbn_epub', 'isbn_mobi',
            'abstract',
            'has_mp3_file', 'has_sync_file',
            'elevenreader_link', 'content_warnings', 'audiences',
            'changed_at', 'read_time', 'pages', 'redakcja',
            'price',
        ]

    def get_price(self, obj):
        if obj.pages is None:
            return None
        return self.context['partner'].get_price(obj.pages)


class PartnerAudiobookSerializer(BookSerializer2):
    price = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'slug', 'title',
            'href', 'url', 'language',
            'authors', 'translators',
            'epochs', 'genres', 'kinds',
            'files',
            'cover',
            'isbn_mp3',
            'abstract',
            'content_warnings', 'audiences',
            'changed_at', 'duration',
            'price',
        ]

    def get_duration(self, obj):
        return obj.get_audiobooks(True)[2]

    def get_files(self, obj):
        def get_for_single(b):
            fs = []
            for m in b.media.filter(type='mp3'):
                fs.append({
                    "name": m.name,
                    "part_name": m.part_name,
                    "url": 'https://wolnelektury.pl' + m.file.url,
                })
            for c in b.get_children():
                fs.extend(get_for_single(c))
            return fs
        return get_for_single(b)

    def get_price(self, obj):
        duration = obj.get_audiobooks(True)[2]
        if not duration:
            return None
        duration /= 60
        return self.context['partner'].get_audio_price(obj.pages)


@method_decorator(never_cache, name='dispatch')
class PartnerBooksView(ListAPIView):
    serializer_class = PartnerBookSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['partner'] = get_object_or_404(models.Partner, key=self.kwargs['key'])
        return ctx

    def get_queryset(self):
        return Book.objects.filter(parent=None).filter(can_sell=True).exclude(pages=None)


@method_decorator(never_cache, name='dispatch')
class PartnerAudiobooksView(ListAPIView):
    serializer_class = PartnerAudiobookSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['partner'] = get_object_or_404(models.Partner, key=self.kwargs['key'])
        return ctx

    def get_queryset(self):
        return Book.objects.exclude(isbn_mp3='')
