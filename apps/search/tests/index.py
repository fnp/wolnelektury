# -*- coding: utf-8 -*-

from __future__ import with_statement

from django.conf import settings
from search import Index, Search, IndexStore, JVM, SearchResult
from catalogue import models
from catalogue.test_utils import WLTestCase
from lucene import PolishAnalyzer, Version
#from nose.tools import raises
from os import path


class BookSearchTests(WLTestCase):
    def setUp(self):
        JVM.attachCurrentThread()
        WLTestCase.setUp(self)
        settings.SEARCH_INDEX = path.join(settings.MEDIA_ROOT, 'search')

        txt = path.join(path.dirname(__file__), 'files/fraszka-do-anusie.xml')
        self.book = models.Book.from_xml_file(txt)

        index = Index()
        index.open()
        try:
            index.index_book(self.book)
        except:
            index.close()

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
        assert len(filter(lambda x: x[1], a[0].hits)) == 1
        print a[0].process_hits()

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
