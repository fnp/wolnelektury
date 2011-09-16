# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.files.base import ContentFile
from catalogue.test_utils import *
from catalogue.models import Book
from dictionary.models import Note


class DictionaryTests(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
        self.book_info = BookInfoStub(
            url=u"http://wolnelektury.pl/example/default-book",
            about=u"http://wolnelektury.pl/example/URI/default_book",
            title=u"Default Book",
            author=PersonStub(("Jim",), "Lazy"),
            kind="X-Kind",
            genre="X-Genre",
            epoch="X-Epoch",
        )

    def test_book_with_fragment(self):
        BOOK_TEXT = """<utwor>
        <opowiadanie>
            <akap><pe><slowo_obce>rose</slowo_obce> --- kind of a flower.</pe></akap>
        </opowiadanie></utwor>
        """

        book = Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

        self.assertEqual(
            len(self.client.get('/przypisy/').context['object_list']),
            1,
            'There should be a note on the note list.')

        self.assertEqual(
            len(self.client.get('/przypisy/a/').context['object_list']),
            0,
            'There should not be a note for the letter A.')

        self.assertEqual(
            len(self.client.get('/przypisy/r/').context['object_list']),
            1,
            'There should be a note for the letter R.')

