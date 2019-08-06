# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from unittest import skipIf
from django.conf import settings
from django.test.utils import override_settings
from catalogue.test_utils import WLTestCase, get_fixture
import tempfile
from catalogue.models import Book
from search.index import Index, Search
import catalogue
import opds


@override_settings(SEARCH_INDEX=tempfile.mkdtemp(prefix='djangotest_search_'))
@skipIf(getattr(settings, 'NO_SEARCH_INDEX', False),
        'Requires search server and NO_SEARCH_INDEX=False.')
class BookSearchTests(WLTestCase):
    def setUp(self):
        WLTestCase.setUp(self)

        index = Index()
        self.search = Search()
        index.delete_query(self.search.index.query(uid="*"))
        index.index.commit()

        self.do_doktora = Book.from_xml_file(
            get_fixture('do-doktora.xml', opds))
        self.do_anusie = Book.from_xml_file(
            get_fixture('fraszka-do-anusie.xml', catalogue))

    # TODO: Add slop option to sunburnt
    # def test_search_perfect_parts(self):
    #     books = self.search.search_phrase("Jakoż hamować")
    #     assert len(books) == 2
    #     for b in books:
    #         b.book_id == self.book.id
    #     a = SearchResult.aggregate(books)
    #     # just one fragment hit.
    #     assert len(a[0].hits) == 1
