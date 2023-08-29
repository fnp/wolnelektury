# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.core.files.base import ContentFile
from catalogue.test_utils import BookInfoStub, PersonStub, info_args, WLTestCase
from catalogue.models import Book
from unittest.mock import patch


class CoverTests(WLTestCase):
    """Checks in parent_cover_changed is properly called."""
    def setUp(self):
        WLTestCase.setUp(self)
        self.TEXT = """<utwor />"""
        self.child = BookInfoStub(
            genre='X-Genre',
            epoch='X-Epoch',
            kind='X-Kind',
            author=PersonStub(("Joe",), "Doe"),
            **info_args("Child")
        )

        self.parent = BookInfoStub(
            genre='X-Genre',
            epoch='X-Epoch',
            kind='X-Kind',
            author=PersonStub(("Jim",), "Lazy"),
            cover_url="http://example.com/cover.jpg",
            parts=[self.child.url],
            **info_args("Parent")
        )

    @patch.object(Book, 'parent_cover_changed', autospec=True)
    def test_simple_import(self, parent_cover_changed):
        child = Book.from_text_and_meta(ContentFile(self.TEXT), self.child)
        parent = Book.from_text_and_meta(ContentFile(self.TEXT), self.parent)
        parent_cover_changed.assert_called_with(child)

        # Now reimport parent.
        parent_cover_changed.reset_mock()
        parent = Book.from_text_and_meta(ContentFile(self.TEXT), self.parent, overwrite=True)
        self.assertEqual(parent_cover_changed.call_count, 0)

        # Now change cover in parent.
        parent_cover_changed.reset_mock()
        self.parent.cover_url = "http://example.com/other-cover.jpg"
        parent = Book.from_text_and_meta(ContentFile(self.TEXT), self.parent, overwrite=True)
        parent_cover_changed.assert_called_with(child)

    @patch.object(Book, 'parent_cover_changed', autospec=True)
    def test_change_cover(self, parent_cover_changed):
        child = Book.from_text_and_meta(ContentFile(self.TEXT), self.child)
        parent = Book.from_text_and_meta(ContentFile(self.TEXT), self.parent)
        parent_cover_changed.assert_called_with(child)

    @patch.object(Book, 'parent_cover_changed', autospec=True)
    def test_new_child(self, parent_cover_changed):
        # Add parent without child first.
        parts, self.parent.parts = self.parent.parts, []
        parent = Book.from_text_and_meta(ContentFile(self.TEXT), self.parent)

        # Now import child and reimport parent.
        child = Book.from_text_and_meta(ContentFile(self.TEXT), self.child)
        self.parent.parts = parts
        parent = Book.from_text_and_meta(ContentFile(self.TEXT), self.parent, overwrite=True)
        parent_cover_changed.assert_called_with(child)

        # Now remove the child.
        parent_cover_changed.reset_mock()
        self.parent.parts = []
        parent = Book.from_text_and_meta(ContentFile(self.TEXT), self.parent, overwrite=True)
        parent_cover_changed.assert_called_with(child)
