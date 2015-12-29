# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.files.base import ContentFile
from catalogue.test_utils import *
from catalogue.models import Book


class DictionaryTests(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
        self.book_info = BookInfoStub(
            author=PersonStub(("Jim",), "Lazy"),
            kind="X-Kind",
            genre="X-Genre",
            epoch="X-Epoch",
            **info_args(u"Default Book")
        )

    def test_book_with_footnote(self):
        BOOK_TEXT = """<utwor>
        <opowiadanie>
            <akap><pe><slowo_obce>rose</slowo_obce> --- kind of a flower.</pe></akap>
            <akap><pe><slowo_obce>rose</slowo_obce> --- kind of a flower.</pe></akap>
            <akap><pe><slowo_obce>rose</slowo_obce> (techn.) --- #FF007F.</pe></akap>
        </opowiadanie></utwor>
        """

        book = Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

        self.assertEqual(
            len(self.client.get('/przypisy/').context['object_list']),
            2,
            'There should be two notes on the note list.')

        self.assertEqual(
            len(self.client.get('/przypisy/?ltr=a').context['object_list']),
            0,
            'There should not be a note for the letter A.')

        self.assertEqual(
            len(self.client.get('/przypisy/?ltr=r').context['object_list']),
            2,
            'Both notes start with the letter R.')

        self.assertEqual(
            len(self.client.get('/przypisy/?qual=techn.').context['object_list']),
            1,
            'There should be a note qualified with \'techn.\' qualifier.')

