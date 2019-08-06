# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from catalogue.test_utils import WLTestCase
from catalogue import models
from oai.handlers import *
from oaipmh.server import *
from os import path
from oaipmh.metadata import MetadataRegistry


class BookMetadataTest(WLTestCase):
    def setUp(self):
        super(BookMetadataTest, self).setUp()
        xml = path.join(path.dirname(__file__), 'files/lubie-kiedy-kobieta.xml')
        self.book = models.Book.from_xml_file(xml)

        xml = path.join(path.dirname(__file__), 'files/antygona.xml')
        self.book2 = models.Book.from_xml_file(xml)

        mr = MetadataRegistry()
        self.catalogue = Catalogue(mr)

        mr.registerWriter('oai_dc', oai_dc_writer)
        nsmap = {'oai_dc': NS_OAIDC, 'dc': NS_DC, 'xsi': NS_XSI}
        self.xml = XMLTreeServer(self.catalogue, mr, nsmap)

    # def test_get_record(self):
    #     self.xml.getRecord(identifier='lubie-kiedy-kobieta', metadataPrefix='oai_dc')
    #     self.xml.listRecords(metadataPrefix='oai_dc')
    #
    # def test_selecting(self):
    #     records, token = self.catalogue.listRecords(**{'set': 'epoch:starozytnosc'})
