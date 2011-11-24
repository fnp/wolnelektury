from __future__ import with_statement

from search import Index, Search
from catalogue import models
from catalogue.test_utils import WLTestCase
from lucene import PolishAnalyzer, Version
#from nose.tools import raises
from os import path


class BookSearchTests(WLTestCase):
    def setUp(self):
        WLTestCase.setUp(self)

        txt = path.join(path.dirname(__file__), 'files/fraszka-do-anusie.xml')
        self.book = models.Book.from_xml_file(txt)

        search = Index() #PolishAnalyzer(Version.LUCENE_34))
        with search:
            search.index_book(self.book)
        print "index: %s" % search

    def test_search(self):
        search = Search()
        bks,_= search.search("wolne")
        self.assertEqual(len(bks), 1)
        self.assertEqual(bks[0].id, 1)
        
        bks,_= search.search("technical_editors: sutkowska")
        self.assertEqual(len(bks), 1)
        self.assertEqual(bks[0].id, 1)
        
