# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.test.utils import override_settings
from catalogue.test_utils import WLTestCase, get_fixture
from catalogue.models import Book
import catalogue
import opds


class BookSearchTests(WLTestCase):
    def setUp(self):
        WLTestCase.setUp(self)

        with override_settings(NO_SEARCH_INDEX=False):
            self.do_doktora = Book.from_xml_file(
                get_fixture('do-doktora.xml', opds))
            self.do_anusie = Book.from_xml_file(
                get_fixture('fraszka-do-anusie.xml', catalogue))

    def test_search_perfect_parts(self):
        response = self.client.get('/szukaj/?q=Jakoż hamować')
        res = response.context['results']
        self.assertEqual(len(res['snippet']), 1)
        for b, s in res['snippet'].items():
             self.assertEqual(b.id, self.do_anusie.id)
