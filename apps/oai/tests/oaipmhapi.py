
import sys
print sys.path

from catalogue.test_utils import WLTestCase
from catalogue import models
from nose.tools import raises
from os import path
from oai.handlers import Catalogue

class BookMetadataTest(WLTestCase):
    def setUp(self):
        super(BookMetadata, self).setUp()
        xml = path.join(path.dirname(__file__), 'files/lubie-kiedy-kobieta.xml')
        self.book = models.Book.from_xml_file(xml)
        self.catalogue = Catalogue()

    def test_get_record(self):
        r = self.catalogue.getRecord(record='lubie-kiedy-kobieta')
        print r
