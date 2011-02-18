# -*- coding: utf-8 -*-

from django.core.files.base import ContentFile

from catalogue.test_utils import *
from catalogue import models

class BookMediaTests(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
        self.file = ContentFile('X')

    def test_diacritics(self):
        bm = models.BookMedia.objects.create(type="ogg", 
                    name="Zażółć gęślą jaźń")
        bm.file.save(bm.name, self.file)
        self.assertEqual(bm.file.name.rsplit('/', 1)[-1], 'zazolc-gesla-jazn.ogg')


    def test_long_name(self):
        bm = models.BookMedia.objects.create(type="ogg", 
                    name="Some very very very very very very very very very very very very very very very very long file name")

        # save twice so Django adds some stuff
        bm.file.save(bm.name, self.file)
        bm.file.save(bm.name, self.file)
        bm.save()

        # reload to see what was really saved
        bm = models.BookMedia.objects.get(pk=bm.pk)
        self.assertEqual(bm.file.size, 1)

