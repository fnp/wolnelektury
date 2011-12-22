# -*- coding: utf-8 -*-
from __future__ import with_statement

from django.core.files.base import ContentFile, File
from catalogue.test_utils import *
from catalogue import models
from librarian import WLURI
from picture.models import Picture

from nose.tools import raises
import tempfile
from os import unlink, path, makedirs


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
        
