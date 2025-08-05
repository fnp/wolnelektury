# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from search.views import get_hints
from search.forms import SearchFilters


class HintView(APIView):
    def get(self, request):
        term = request.query_params.get('q')
        hints = get_hints(term, request.user)
        return Response(hints)


class SearchView(APIView):
    def get(self, request):
        term = self.request.query_params.get('q')
        f = SearchFilters({'q': term})
        r = {}
        if f.is_valid():
            r = f.results()
        return Response(r)

class BookSearchView(ListAPIView):
    def get_queryset(self, request):
        term = self.request.query_params.get('q')

class TextSearchView(ListAPIView):
    def get_queryset(self, request):
        term = self.request.query_params.get('q')
