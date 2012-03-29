# -*- coding: utf-8 -*-
from __future__ import with_statement

from os import path
from django.test import TestCase
from picture.models import Picture


class PictureTest(TestCase):
    
    def test_import(self):
        picture = Picture.from_xml_file(path.join(path.dirname(__file__), "files/kandinsky-composition-viii.xml"))

        motifs = set([tag.name for tag in picture.tags if tag.category == 'theme'])
        assert motifs == set([u'nieporządek']), 'theme tags are wrong. %s' % motifs

        picture.delete()

    def test_import_with_explicit_image(self):
        picture = Picture.from_xml_file(path.join(path.dirname(__file__), "files/kandinsky-composition-viii.xml"),
                                        path.join(path.dirname(__file__), "files/kandinsky-composition-viii.png"))

        picture.delete()
        
