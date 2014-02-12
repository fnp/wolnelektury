# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import with_statement

from os import path
from picture.models import Picture
from catalogue.test_utils import WLTestCase


class PictureTest(WLTestCase):
    
    def test_import(self):
        picture = Picture.from_xml_file(path.join(path.dirname(__file__), "files/kandinsky-composition-viii.xml"))

        motifs = set([tag.name for tag in picture.tags if tag.category == 'theme'])
        assert motifs == set([u'nieporządek']), 'theme tags are wrong. %s' % motifs

        picture.delete()

    def test_import_with_explicit_image(self):
        picture = Picture.from_xml_file(path.join(path.dirname(__file__), "files/kandinsky-composition-viii.xml"),
                                        path.join(path.dirname(__file__), "files/kandinsky-composition-viii.png"))

        picture.delete()
        

    def test_import_2(self):
        picture = Picture.from_xml_file(path.join(path.dirname(__file__), "files/pejzaz-i-miasto-krzyzanowski-chmury.xml"),
                                        path.join(path.dirname(__file__), "files/pejzaz-i-miasto-krzyzanowski-chmury.jpg"),
                                        overwrite=True)
        cats = set([t.category for t in picture.tags])
        assert 'genre' in cats
        assert 'kind' in cats

