# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from catalogue import models
from catalogue.templatetags import catalogue_tags
from catalogue.test_utils import *
from django.core.files.base import ContentFile


class BookDescTests(WLTestCase):
    """ tests book_title template tag """

    def setUp(self):
        WLTestCase.setUp(self)
        authors = PersonStub(("Common",), "Man"), PersonStub(("Jane",), "Doe")

        child_info = BookInfoStub(authors=authors, genre="Genre", epoch='Epoch', kind="Kind",
                                  **info_args("Child"))
        parent_info = BookInfoStub(authors=authors, genre="Genre", epoch='Epoch', kind="Kind",
                                   parts=[child_info.url],
                                   **info_args("Parent"))

        self.child = models.Book.from_text_and_meta(ContentFile('<utwor/>'), child_info)
        models.Book.from_text_and_meta(ContentFile('<utwor/>'), parent_info)
        self.child = models.Book.objects.get(pk=self.child.pk)

    def test_book_desc(self):
        """ book description should return authors, ancestors, book """
        self.assertEqual(catalogue_tags.book_title(self.child), 'Jane Doe, Common Man, Parent, Child')
