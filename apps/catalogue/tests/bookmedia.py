# -*- coding: utf-8 -*-

from django.core.files.base import ContentFile

from catalogue.test_utils import *
from catalogue import models

class BookMediaTests(WLTestCase):

    def test_long_name(self):
        file = ContentFile('X')
        bm = models.BookMedia.objects.create(type="ogg", 
                    name="Some very very very very very very very very very very very very very very very very long file name")
        bm.file.save(bm.name, file)
        bm.save()

        # reload to see what was really saved
        bm = models.BookMedia.objects.get(pk=bm.pk)
        self.assertEqual(bm.file.size, 1)

