# -*- coding: utf-8 -*-
from django.core.files.base import ContentFile
from catalogue.test_utils import *
from catalogue import models

from nose.tools import raises


class BookImportLogicTests(WLTestCase):

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
        self.assertEqual(book.slug, "default-book")
        self.assert_(book.parent is None)
        self.assertFalse(book.has_html_file())

        # no fragments generated
        self.assertEqual(book.fragments.count(), 0)

        # TODO: this should be filled out probably...
        self.assertEqual(book.wiki_link, '')
        self.assertEqual(book.gazeta_link, '')
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

        self.assert_(('theme', 'love') in [ (tag.category, tag.slug) for tag in book.fragments.all()[0].tags ])

    def test_book_with_empty_theme(self):
        """ empty themes should be ignored """

        BOOK_TEXT = """<utwor>
        <opowiadanie>
            <akap><begin id="m01" /><motyw id="m01"> , Love , , </motyw>Ala ma kota<end id="m01" /></akap>
        </opowiadanie></utwor>
        """

        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.assert_([('theme', 'love')],
                         [ (tag.category, tag.slug) for tag in book.fragments.all()[0].tags.filter(category='theme') ])

    def test_book_with_no_theme(self):
        """ fragments with no themes shouldn't be created at all """

        BOOK_TEXT = """<utwor>
        <opowiadanie>
            <akap><begin id="m01" /><motyw id="m01"></motyw>Ala ma kota<end id="m01" /></akap>
        </opowiadanie></utwor>
        """

        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.assertEqual(book.fragments.count(), 0)
        self.assertEqual(book.tags.filter(category='theme').count(), 0)

    @raises(ValueError)
    def test_book_with_invalid_slug(self):
        """ Book with invalid characters in slug shouldn't be imported """
        self.book_info.url = "http://wolnelektury.pl/example/default_book"
        BOOK_TEXT = "<utwor />"
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

    def test_book_replace_title(self):
        BOOK_TEXT = """<utwor />"""
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.book_info.title = u"Extraordinary"
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info, overwrite=True)

        tags = [ (tag.category, tag.slug) for tag in book.tags ]
        tags.sort()

        self.assertEqual(tags, self.expected_tags)

    def test_book_replace_author(self):
        BOOK_TEXT = """<utwor />"""
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.book_info.author = PersonStub(("Hans", "Christian"), "Andersen")
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info, overwrite=True)

        tags = [ (tag.category, tag.slug) for tag in book.tags ]
        tags.sort()

        self.expected_tags.remove(('author', 'jim-lazy'))
        self.expected_tags.append(('author', 'hans-christian-andersen'))
        self.expected_tags.sort()

        self.assertEqual(tags, self.expected_tags)

        # the old tag shouldn't disappear
        models.Tag.objects.get(slug="jim-lazy", category="author")

    def test_book_remove_fragment(self):
        BOOK_TEXT = """<utwor>
        <opowiadanie>
            <akap>
                <begin id="m01" /><motyw id="m01">Love</motyw>Ala ma kota<end id="m01" />
                <begin id="m02" /><motyw id="m02">Hatred</motyw>To kot Ali<end id="m02" />
            </akap>
        </opowiadanie></utwor>
        """
        BOOK_TEXT_AFTER = """<utwor>
        <opowiadanie>
            <akap>
                <begin id="m01" /><motyw id="m01">Love</motyw>Ala ma kota<end id="m01" />
                To kot Ali
            </akap>
        </opowiadanie></utwor>
        """

        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.assertEqual(book.fragments.count(), 2)
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT_AFTER), self.book_info, overwrite=True)
        self.assertEqual(book.fragments.count(), 1)

    def test_multiple_tags(self):
        BOOK_TEXT = """<utwor />"""
        self.book_info.authors = self.book_info.author, PersonStub(("Joe",), "Dilligent"),
        self.book_info.kinds = self.book_info.kind, 'Y-Kind',
        self.book_info.genres = self.book_info.genre, 'Y-Genre',
        self.book_info.epochs = self.book_info.epoch, 'Y-Epoch',

        self.expected_tags.extend([
           ('author', 'joe-dilligent'),
           ('genre', 'y-genre'),
           ('epoch', 'y-epoch'),
           ('kind', 'y-kind'),
        ])
        self.expected_tags.sort()

        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        tags = [ (tag.category, tag.slug) for tag in book.tags ]
        tags.sort()

        self.assertEqual(tags, self.expected_tags)


class ChildImportTests(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
        self.child_info = BookInfoStub(
            genre='X-Genre',
            epoch='X-Epoch',
            kind='X-Kind',
            author=PersonStub(("Joe",), "Doe"),
            **info_args("Child")
        )

        self.parent_info = BookInfoStub(
            genre='X-Genre',
            epoch='X-Epoch',
            kind='X-Kind',
            author=PersonStub(("Jim",), "Lazy"),
            parts=[self.child_info.url],
            **info_args("Parent")
        )

    def test_child_replace(self):
        PARENT_TEXT = """<utwor />"""
        CHILD_TEXT = """<utwor>
        <opowiadanie>
            <akap><begin id="m01" /><motyw id="m01">Pies</motyw>Ala ma kota<end id="m01" /></akap>
        </opowiadanie></utwor>
        """
        child = models.Book.from_text_and_meta(ContentFile(CHILD_TEXT), self.child_info)
        parent = models.Book.from_text_and_meta(ContentFile(PARENT_TEXT), self.parent_info)
        CHILD_TEXT = """<utwor>
        <opowiadanie>
            <akap><begin id="m01" /><motyw id="m01">Kot</motyw>Ala ma kota<end id="m01" /></akap>
        </opowiadanie></utwor>
        """
        child = models.Book.from_text_and_meta(ContentFile(CHILD_TEXT), self.child_info, overwrite=True)

        themes = self.client.get(parent.get_absolute_url()).context['book_themes']

        self.assertEqual(['Kot'], [tag.name for tag in themes],
                        'wrong related theme list')
