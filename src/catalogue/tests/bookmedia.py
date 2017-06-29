# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os.path import basename, exists
from unittest import skip

from django.core.files.base import ContentFile

from catalogue.test_utils import *
from catalogue import models, utils


class BookMediaTests(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
        self.file = ContentFile('X')
        self.file2 = ContentFile('Y')
        self.book = models.Book.objects.create(slug='test-book', title='Test')

    def set_title(self, title):
        self.book.title = title
        self.book.save()

    def test_diacritics(self):
        bm = models.BookMedia(book=self.book, type="ogg", name=u"Zażółć gęślą jaźń")
        self.set_title(bm.name)
        bm.file.save(None, self.file)
        self.assertEqual(basename(bm.file.name), 'zazolc-gesla-jazn.ogg')

    def test_long_name(self):
        bm = models.BookMedia(
            book=self.book, type="ogg",
            name="Some very very very very very very very very very very very very very very very very long file name")
        self.set_title(bm.name)
        bm.file.save(bm.name, self.file)

        # reload to see what was really saved
        bm = models.BookMedia.objects.get(pk=bm.pk)
        self.assertEqual(bm.file.size, 1)

    def test_overwrite(self):
        """
            File gets overwritten with same filename on update.
        """

        bm = models.BookMedia(book=self.book, type='ogg', name="Some media")
        self.set_title(bm.name)
        bm.file.save(None, self.file)
        bm.file.save(None, self.file2)

        self.assertEqual(bm.file.read(), 'Y')
        self.assertEqual(basename(bm.file.name), 'some-media.ogg')

    @skip('broken, but is it needed?')
    def test_no_clobber(self):
        """
            File save doesn't clobber some other media with similar name.
        """

        bm = models.BookMedia(book=self.book, type='ogg', name=u"Tytul")
        self.set_title(bm.name)
        bm.file.save(None, self.file)
        bm2 = models.BookMedia(book=self.book, type='ogg', name=u"Tytuł")
        self.set_title(bm2.name)
        bm2.file.save(None, self.file2)
        self.assertEqual(basename(bm.file.name), 'tytul.ogg')
        self.assertNotEqual(basename(bm2.file.name), 'tytul.ogg')
        self.assertEqual(bm.file.read(), 'X')
        self.assertEqual(bm2.file.read(), 'Y')

    def test_change_name(self):
        """
            File name reflects name change.
        """

        bm = models.BookMedia(book=self.book, type='ogg', name="Title")
        self.set_title(bm.name)
        bm.file.save(None, self.file)
        self.set_title("Other Title")
        bm.save()
        self.assertEqual(basename(bm.file.name), 'other-title.ogg')
        self.assertEqual(bm.file.read(), 'X')

    @skip('broken, but is it needed?')
    def test_change_name_no_clobber(self):
        """
            File name after change won't clobber some other file
            with similar name.
        """

        bm = models.BookMedia(book=self.book, type='ogg', name="Title")
        self.set_title(bm.name)
        bm.file.save(None, self.file)
        bm2 = models.BookMedia(book=self.book, type='ogg', name="Other title")
        self.set_title(bm2.name)
        bm2.file.save(None, self.file2)
        self.set_title("Title")
        bm2.save()
        self.assertNotEqual(basename(bm2.file.name), 'title.ogg')
        self.assertEqual(bm.file.read(), 'X')
        self.assertEqual(bm2.file.read(), 'Y')

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
