# -*- coding: utf-8 -*-
from django.core.files.base import ContentFile
from catalogue.test_utils import *
from catalogue import models

class BookImportLogicTests(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
        self.book_info = BookInfoStub(
            url=u"http://wolnelektury.pl/example/default_book",
            about=u"http://wolnelektury.pl/example/URI/default_book",
            title=u"Default Book",
            author=PersonStub(("Jim",), "Lazy"),
            kind="X-Kind",
            genre="X-Genre",
            epoch="X-Epoch",
        )

        self.expected_tags = [
           ('author', 'jim-lazy'),
           ('genre', 'x-genre'),
           ('epoch', 'x-epoch'),
           ('kind', 'x-kind'),
        ]
        self.expected_tags.sort()

    def test_empty_book(self):
        BOOK_TEXT = "<utwor />"
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

        self.assertEqual(book.title, "Default Book")
        self.assertEqual(book.slug, "default_book")
        self.assert_(book.parent is None)
        self.assertFalse(book.has_html_file())

        # no fragments generated
        self.assertEqual(book.fragments.count(), 0)

        # TODO: this should be filled out probably...
        self.assertEqual(book.wiki_link, '')
        self.assertEqual(book.gazeta_link, '')
        self.assertEqual(book._short_html, '')
        self.assertEqual(book.description, '')

        tags = [ (tag.category, tag.slug) for tag in book.tags ]
        tags.sort()

        self.assertEqual(tags, self.expected_tags)

    def test_not_quite_empty_book(self):
        """ Not empty, but without any real text.

        Should work like any other non-empty book.
        """

        BOOK_TEXT = """<utwor>
        <liryka_l>
            <nazwa_utworu>Nic</nazwa_utworu>
        </liryka_l></utwor>
        """

        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.assertTrue(book.has_html_file())

    def test_book_with_fragment(self):
        BOOK_TEXT = """<utwor>
        <opowiadanie>
            <akap><begin id="m01" /><motyw id="m01">Love</motyw>Ala ma kota<end id="m01" /></akap>
        </opowiadanie></utwor>
        """

        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.assertTrue(book.has_html_file())

        self.assertEqual(book.fragments.count(), 1)
        self.assertEqual(book.fragments.all()[0].text, u'<p class="paragraph">Ala ma kota</p>\n')

        self.assert_(('theme', 'love') in [ (tag.category, tag.slug) for tag in book.tags ])

    def test_book_replace_title(self):
        BOOK_TEXT = """<utwor />"""
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.book_info.title = u"Extraordinary"
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

        tags = [ (tag.category, tag.slug) for tag in book.tags ]
        tags.sort()

        self.assertEqual(tags, self.expected_tags)

    def test_book_replace_author(self):
        BOOK_TEXT = """<utwor />"""
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.book_info.author = PersonStub(("Hans", "Christian"), "Andersen")
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

        tags = [ (tag.category, tag.slug) for tag in book.tags ]
        tags.sort()

        self.expected_tags.remove(('author', 'jim-lazy'))
        self.expected_tags.append(('author', 'hans-christian-andersen'))
        self.expected_tags.sort()

        self.assertEqual(tags, self.expected_tags)

        # the old tag should disappear
        self.assertRaises(models.Tag.DoesNotExist, models.Tag.objects.get,
                    slug="jim-lazy", category="author")
