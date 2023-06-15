# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os.path import basename, exists
from unittest import skip

from django.core.files.base import ContentFile, File

from catalogue.test_utils import *
from catalogue import models, utils


class BookMediaTests(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
        self.file = ContentFile(b'X')
        self.file2 = ContentFile(b'Y')
        self.book = models.Book.objects.create(slug='test-book', title='Test')
        with open(join(dirname(__file__), "files/fraszka-do-anusie.xml")) as f:
            self.book.xml_file.save(None, File(f))

    def set_title(self, title):
        self.book.title = title
        self.book.save()

    def test_overwrite(self):
        """
            File gets overwritten with same filename on update.
        """

        bm = models.BookMedia(book=self.book, type='ogg', name="Some media")
        self.set_title(bm.name)
        bm.file.save(None, self.file)
        bm.file.save(None, self.file2)

        self.assertEqual(bm.file.read(), b'Y')
        self.assertEqual(basename(bm.file.name), 'test-book.ogg')

    def test_zip_audiobooks(self):
        paths = [
            (None, join(dirname(__file__), "files/fraszka-do-anusie.xml")),
            (None, join(dirname(__file__), "files/fraszki.xml")),
            ]

        url = utils.create_zip(paths, 'test-zip-slug')
        self.assertEqual("zip/test-zip-slug.zip", url)
        self.assertTrue(exists(join(settings.MEDIA_ROOT, url)))

        utils.remove_zip('test-zip-slug')
        self.assertFalse(exists(join(settings.MEDIA_ROOT, url)))

    def test_remove_zip_on_media_change(self):
        bm = models.BookMedia(book=self.book, type='ogg', name="Title")
        self.set_title(bm.name)
        bm.file.save(None, self.file)
        bm.save()

        zip_url = self.book.zip_audiobooks('ogg')
        self.assertEqual('zip/'+self.book.slug+'_ogg.zip', zip_url)
        self.assertTrue(exists(join(settings.MEDIA_ROOT, zip_url)))

        bm2 = models.BookMedia(book=self.book, type='ogg', name="Other title")
        self.set_title(bm2.name)
        bm2.file.save(None, self.file2)
        self.set_title("Title")
        bm2.save()
        # was the audiobook zip deleted?
        self.assertFalse(exists(join(settings.MEDIA_ROOT, zip_url)))
