# -*- coding: utf-8 -*-
from django.conf import settings
from django.test.utils import override_settings
from catalogue.test_utils import WLTestCase
from lucene import PolishAnalyzer, Version
from os import path
import tempfile
from catalogue import models
from search import Search, SearchResult


@override_settings(
    SEARCH_INDEX = tempfile.mkdtemp(prefix='djangotest_search_'),
)
class BookSearchTests(WLTestCase):
    def setUp(self):
        WLTestCase.setUp(self)

        txt = path.join(path.dirname(__file__), 'files/fraszka-do-anusie.xml')
        with self.settings(NO_SEARCH_INDEX=False):
            self.book = models.Book.from_xml_file(txt)
        self.search = Search()

    def test_search_perfect_book_author(self):
        books = self.search.search_perfect_book("sęp szarzyński")
        assert len(books) == 1
        assert books[0].book_id == self.book.id

    def test_search_perfect_book_title(self):
        books = self.search.search_perfect_book("fraszka anusie")
        assert len(books) == 1
        assert books[0].book_id == self.book.id

    def test_search_perfect_parts(self):
        books = self.search.search_perfect_parts("Jakoż hamować")
        assert len(books) == 2
        for b in books:
            b.book_id == self.book.id
        a = SearchResult.aggregate(books)
        # just one fragment hit.
        assert len(a[0].hits) == 1

    def test_search_perfect_author_title(self):
        books = self.search.search_perfect_book("szarzyński anusie")
        assert books == []

        books = self.search.search_book("szarzyński anusie")
        assert len(books) == 1

        books = self.search.search_book("szarzyński fraszka")
        assert len(books) == 1

    def test_search_everywhere(self):
        books = self.search.search_everywhere("szarzyński kochanek")
        print 'szarzyński kochanek %s' % [b.hits for b in books]

        books = self.search.search_everywhere("szarzyński narcyz")
        print 'szarzyński narcyz %s' % [b.hits for b in books]

        books = self.search.search_everywhere("anusie narcyz")
        print 'anusie narcyz %s' % [b.hits for b in books]

        # theme content cross
        books = self.search.search_everywhere("wzrok  boginie")
        print 'wzrok boginie %s' % [b.hits for b in books]

        books = self.search.search_everywhere("anusie płynęły zdroje")
        print 'anusie płynęły zdroje %s' % [b.hits for b in books]
