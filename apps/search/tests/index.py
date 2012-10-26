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
        self.search = Search()
        index.delete_query(self.search.index.query(uid="*"))
        index.index.commit()

        with self.settings(NO_SEARCH_INDEX=False):
            self.do_doktora = Book.from_xml_file(
                get_fixture('do-doktora.xml', opds))
            self.do_anusie = Book.from_xml_file(
                get_fixture('fraszka-do-anusie.xml', catalogue))

    def test_search_perfect_book_author(self):
        books = self.search.search_books(self.search.index.query(authors=u"sęp szarzyński"))
        assert len(books) == 1
        assert books[0].id == self.do_anusie.id

        # here we lack slop functionality as well
    def test_search_perfect_book_title(self):
        books = self.search.search_books(self.search.index.query(title=u"fraszka do anusie"))
        assert len(books) == 1
        assert books[0].id == self.do_anusie.id

    # TODO: Add slop option to sunburnt
    # def test_search_perfect_parts(self):
    #     books = self.search.search_phrase(u"Jakoż hamować")
    #     assert len(books) == 2
    #     for b in books:
    #         b.book_id == self.book.id
    #     a = SearchResult.aggregate(books)
    #     # just one fragment hit.
    #     assert len(a[0].hits) == 1

