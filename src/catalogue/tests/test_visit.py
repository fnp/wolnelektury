# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from catalogue import models
from catalogue.test_utils import BookInfoStub, PersonStub, WLTestCase, info_args
from django.core.files.base import ContentFile


class VisitTest(WLTestCase):
    """Simply create some objects and visit some views."""

    def setUp(self):
        WLTestCase.setUp(self)
        author = PersonStub(("Jane",), "Doe")
        book_info = BookInfoStub(author=author, genre="Sielanka",
            epoch='Epoch', kind="Kind", **info_args("A book"))
        self.book = models.Book.from_text_and_meta(ContentFile('''
            <utwor>
            <opowiadanie>
                <akap>
                    <begin id="b1" />
                    <motyw id="m1">Sielanka</motyw>
                    Test
                    <end id="e1" />
                </akap>
            </opowiadanie>
            </utwor>
            '''), book_info)
        self.collection = models.Collection.objects.create(
            title='Biblioteczka Boya', slug='boy', book_slugs='a-book')

    def test_visit_urls(self):
        """ book description should return authors, ancestors, book """
        url_map = {
            200: [
                '',
                'lektury/',
                'lektury/boy/',
                'nowe/',
                'lektura/a-book/',
                'lektura/a-book.html',
                'lektura/a-book/motyw/sielanka/',
                'motyw/sielanka/',
                'sielanka/',
                'autor/jane-doe/',
                'daisy/',
                # 'autor/jane-doe/gatunek/genre/',
                # 'autor/jane-doe/gatunek/genre/motyw/sielanka/',
                ],
            404: [
                'lektury/nonexistent/',  # Nonexistent Collection.
                'lektura/nonexistent/',  # Nonexistent Book.
                'lektura/nonexistent.html',  # Nonexistent Book's HTML.
                'lektura/nonexistent/motyw/sielanka/',  # Nonexistent Book's theme.
                'lektura/a-book/motyw/nonexistent/',  # Nonexistent theme in a Book.
                'autor/nonexistent/',  # Nonexistent author.
                'motyw/nonexistent/',  # Nonexistent theme.
                'zh.json',  # Nonexistent language.
                ]
            }
        prefix = '/katalog/'
        for expected_status, urls in url_map.items():
            for url in urls:
                status = self.client.get(prefix + url).status_code
                self.assertEqual(
                    status, expected_status,
                    "Wrong status code for '%s'. Expected %d, got %d." % (prefix + url, expected_status, status))
