# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.core.files.base import ContentFile
from catalogue.test_utils import *
from catalogue.models import Book
from django.contrib.auth.models import User


class DictionaryTests(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
        self.book_info = BookInfoStub(
            author=PersonStub(("Jim",), "Lazy"),
            kind="X-Kind",
            genre="X-Genre",
            epoch="X-Epoch",
            **info_args("Default Book")
        )
        self.user = User.objects.create(username='test')
        self.user.set_password('test')
        self.user.save()

    def test_book_with_footnote(self):
        book_text = b"""<utwor>
        <opowiadanie>
            <akap><pe><slowo_obce>rose</slowo_obce> --- kind of a flower.</pe></akap>
            <akap><pe><slowo_obce>rose</slowo_obce> --- kind of a flower.</pe></akap>
            <akap><pe><slowo_obce>rose</slowo_obce> (techn.) --- #FF007F.</pe></akap>
        </opowiadanie></utwor>
        """

        book = Book.from_text_and_meta(ContentFile(book_text), self.book_info)
        self.client.login(username='test', password='test')

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
