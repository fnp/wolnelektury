# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
import catalogue.models
import catalogue.api.serializers
from search.views import get_hints
from search.forms import SearchFilters


class HintView(APIView):
    def get(self, request):
        term = request.query_params.get('q')
        hints = get_hints(term, request.user)
        for h in hints:
            if h.get('img'):
                h['img'] = request.build_absolute_uri(h['img'])
        return Response(hints)


class SearchView(APIView):
    def get(self, request):
        term = self.request.query_params.get('q')
        f = SearchFilters({'q': term})
        if f.is_valid():
            r = f.results()
            res = {}
            rl = res['author'] = []
            c = {'request': request}
            for item in r['author']:
                rl.append(
                    catalogue.api.serializers.AuthorSerializer(item, context=c).data
                )
            rl = res['genre'] = []
            for item in r['genre']:
                rl.append(
                    catalogue.api.serializers.GenreSerializer(item, context=c).data
                )
            rl = res['theme'] = []
            for item in r['theme']:
                rl.append(
                    catalogue.api.serializers.ThemeSerializer(item, context=c).data
                )

        return Response(res)


class BookSearchView(ListAPIView):
    serializer_class = catalogue.api.serializers.BookSerializer2

    def get_queryset(self):
        term = self.request.query_params.get('q')
        f = SearchFilters({'q': term})
        if f.is_valid():
            r = f.results()
            return r['book']
        return []



class SnippetSerializer(serializers.ModelSerializer):
    anchor = serializers.CharField(source='sec')
    headline = serializers.CharField()

    class Meta:
        model = catalogue.models.Snippet
        fields = ['anchor', 'headline']


class BookSnippetsSerializer(serializers.Serializer):
    book = catalogue.api.serializers.BookSerializer2()
    snippets = SnippetSerializer(many=True)


class TextSearchView(ListAPIView):
    serializer_class = BookSnippetsSerializer

    def get_queryset(self):
        term = self.request.query_params.get('q')
        f = SearchFilters({'q': term})
        if f.is_valid():
            r = f.results()
            r = list({
                'book': book,
                'snippets': snippets
            } for (book, snippets) in r['snippet'].items())
            return r
        return []

