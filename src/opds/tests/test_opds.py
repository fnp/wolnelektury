# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from lxml import etree
from django.conf import settings
import catalogue
from catalogue.test_utils import WLTestCase, get_fixture
from catalogue.models import Book
from librarian import WLURI, XMLNamespace

AtomNS = XMLNamespace("http://www.w3.org/2005/Atom")


class OpdsSearchTests(WLTestCase):
    """Tests search feed in OPDS.."""
    def setUp(self):
        WLTestCase.setUp(self)

        self.do_doktora = Book.from_xml_file(
            get_fixture('do-doktora.xml'))
        self.do_anusie = Book.from_xml_file(
            get_fixture('fraszka-do-anusie.xml', catalogue))

    def assert_finds(self, query, books):
        """Takes a query and tests against books expected to be found."""
        tree = etree.fromstring(
            self.client.get('/opds/search/?%s' % query).content)
        elem_ids = tree.findall('.//%s/%s' % (AtomNS('entry'), AtomNS('id')))
        slugs = [WLURI.from_text(elem.text).slug for elem in elem_ids]
        self.assertEqual(set(slugs), set(b.slug for b in books), "OPDS search '%s' failed." % query)

    def test_opds_search_simple(self):
        """Do a simple q= test, also emulate dumb OPDS clients."""
        both = {self.do_doktora, self.do_anusie}
        self.assert_finds('q=fraszka', both)
        self.assert_finds('q=fraszka&author={opds:author}', both)

    def test_opds_search_title(self):
        """Search by title."""
        both = {self.do_doktora, self.do_anusie}
        self.assert_finds('title=fraszka', both)
        self.assert_finds('title=fraszka', both)
        self.assert_finds('q=title:doktora', [self.do_doktora])

    def test_opds_search_author(self):
        """Search by author."""
        self.assert_finds('q=fraszka&author=Kochanowski', [self.do_doktora])
        self.assert_finds('q=fraszka+author:Kochanowski', [self.do_doktora])
        self.assert_finds('q=Kochanowski', [self.do_doktora])

    def test_opds_search_translator(self):
        """Search by translator."""
        self.assert_finds('q=fraszka&translator=Fikcyjny', [self.do_doktora])
        self.assert_finds('q=fraszka+translator:Fikcyjny', [self.do_doktora])
        self.assert_finds('q=Fikcyjny', [self.do_doktora])
