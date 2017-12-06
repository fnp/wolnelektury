# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from mock import Mock
from catalogue.models import Book, Tag
from random import randint, choice


class Search(Mock):
    """
    Search mock for development without setting up Solr.

    Instead of connecting to an actual search server, it returns
    some random results for any query.
    """
    class MockIndex(Mock):
        def analyze(*args, **kwargs):
            return []

    index = MockIndex()

    @staticmethod
    def _find_some_books(query_terms=None, max_results=20):
        from .index import SearchResult

        qs = Book.objects.order_by('?')
        results = []
        for book in qs[:randint(1, max_results)]:
            doc = {
                'score': randint(0, 100),
                'book_id': book.pk,
                'published_date': randint(1000, 1920),
                }
            res = SearchResult(doc, how_found='mock', query_terms=query_terms)
            results.append(res)
        return results

    # WTF
    def search_books(self, query, filters=None, max_results=10):
        return self._find_some_books(max_results=max_results)

    def search_everywhere(self, searched, query_terms=None):
        return []

    def hint_tags(self, query, pdcounter=True, prefix=True):
        return Tag.objects.exclude(category='set').order_by('?')[:randint(1, 10)]

    def hint_books(self, prefix):
        return Book.objects.order_by('?')[:randint(1, 10)]
