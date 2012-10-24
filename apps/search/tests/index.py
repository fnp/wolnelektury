# -*- coding: utf-8 -*-
from django.conf import settings
from django.test.utils import override_settings
from catalogue.test_utils import WLTestCase, get_fixture
from os import path
import tempfile
from catalogue.models import Book, Tag
from search import Index, Search, SearchResult
import catalogue
import opds


@override_settings(
    SEARCH_INDEX = tempfile.mkdtemp(prefix='djangotest_search_'),
)
class BookSearchTests(WLTestCase):
    def setUp(self):
        WLTestCase.setUp(self)

        index = Index()
        index.index.delete_all()
        index.index.commit()

        with self.settings(NO_SEARCH_INDEX=False):
            self.do_doktora = Book.from_xml_file(
                get_fixture('do-doktora.xml', opds))
            self.do_anusie = Book.from_xml_file(
                get_fixture('fraszka-do-anusie.xml', catalogue))

        self.search = Search()

    def test_search_perfect_book_author(self):
        books = self.search.search_books(self.search.index.query(authors=u"sęp szarzyński"))
        assert len(books) == 1
        assert books[0].book_id == self.book.id

    def test_search_perfect_book_title(self):
        books = self.search.search_books(self.search.index.query(u"fraszka anusie"))
        assert len(books) == 1
        assert books[0].book_id == self.book.id

    def test_search_perfect_parts(self):
        books = self.search.search_phrase(u"Jakoż hamować")
        assert len(books) == 2
        for b in books:
            b.book_id == self.book.id
        a = SearchResult.aggregate(books)
        # just one fragment hit.
        assert len(a[0].hits) == 1

    def test_search_perfect_author_title(self):
        books = self.search.search_books(self.search.index.query(authors=u"szarzyński anusie"))
        assert books == []

        
