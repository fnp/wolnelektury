# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings

from django.core.files.base import ContentFile
from catalogue.test_utils import *
from catalogue import models
from librarian import WLURI

from nose.tools import raises
from os import path, makedirs

class BookImportLogicTests(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
        self.book_info = BookInfoStub(
            url=WLURI.from_slug(u"default-book"),
            about=u"http://wolnelektury.pl/example/URI/default_book",
            title=u"Default Book",
            author=PersonStub(("Jim",), "Lazy"),
            kind="X-Kind",
            genre="X-Genre",
            epoch="X-Epoch",
            language=u"pol",
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
        self.book_info.url = WLURI.from_slug(u"default_book")
        BOOK_TEXT = "<utwor />"
        models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

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

    def test_child(self):
        TEXT = """<utwor />"""
        child = models.Book.from_text_and_meta(ContentFile(TEXT), self.child_info)
        parent = models.Book.from_text_and_meta(ContentFile(TEXT), self.parent_info)
        author = parent.tags.get(category='author')
        books = self.client.get(author.get_absolute_url()).context['object_list']
        self.assertEqual(len(books), 1,
                        "Only parent book should be visible on author's page")

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
        themes = parent.related_themes()
        self.assertEqual(['Kot'], [tag.name for tag in themes],
                        'wrong related theme list')


class TreeImportTest(WLTestCase):
    def setUp(self):
        WLTestCase.setUp(self)
        self.child_info = BookInfoStub(
            genre='X-Genre',
            epoch='X-Epoch',
            kind='X-Kind',
            author=PersonStub(("Joe",), "Doe"),
            **info_args("Child")
        )
        self.CHILD_TEXT = """<utwor>
        <opowiadanie>
            <akap><begin id="m01" /><motyw id="m01">Pies</motyw>
                Ala ma kota<end id="m01" /></akap>
        </opowiadanie></utwor>
        """
        self.child = models.Book.from_text_and_meta(
            ContentFile(self.CHILD_TEXT), self.child_info)

        self.book_info = BookInfoStub(
            genre='X-Genre',
            epoch='X-Epoch',
            kind='X-Kind',
            author=PersonStub(("Joe",), "Doe"),
            parts=[self.child_info.url],
            **info_args("Book")
        )
        self.BOOK_TEXT = """<utwor />"""
        self.book = models.Book.from_text_and_meta(
            ContentFile(self.BOOK_TEXT), self.book_info)

        self.parent_info = BookInfoStub(
            genre='X-Genre',
            epoch='X-Epoch',
            kind='X-Kind',
            author=PersonStub(("Jim",), "Lazy"),
            parts=[self.book_info.url],
            **info_args("Parent")
        )
        self.PARENT_TEXT = """<utwor />"""
        self.parent = models.Book.from_text_and_meta(
            ContentFile(self.PARENT_TEXT), self.parent_info)

    def test_ok(self):
        self.assertEqual(
                list(self.client.get('/katalog/gatunek/x-genre/'
                    ).context['object_list']),
                [self.parent],
                u"There should be only parent on common tag page."
            )
        pies = models.Tag.objects.get(slug='pies')
        self.assertEqual(self.parent.theme_counter, {pies.pk: 1},
                u"There should be child theme in parent theme counter."
            )
        epoch = models.Tag.objects.get(slug='x-epoch')
        self.assertEqual(epoch.book_count, 1,
                u"There should be only parent in common tag's counter."
            )

    def test_child_republish(self):
        CHILD_TEXT = """<utwor>
        <opowiadanie>
            <akap><begin id="m01" /><motyw id="m01">Pies, Kot</motyw>
                Ala ma kota<end id="m01" /></akap>
        </opowiadanie></utwor>
        """
        models.Book.from_text_and_meta(
            ContentFile(CHILD_TEXT), self.child_info, overwrite=True)
        self.assertEqual(
                list(self.client.get('/katalog/gatunek/x-genre/'
                    ).context['object_list']),
                [self.parent],
                u"There should only be parent on common tag page."
            )
        pies = models.Tag.objects.get(slug='pies')
        kot = models.Tag.objects.get(slug='kot')
        self.assertEqual(self.parent.theme_counter, {pies.pk: 1, kot.pk: 1},
                u"There should be child themes in parent theme counter."
            )
        epoch = models.Tag.objects.get(slug='x-epoch')
        self.assertEqual(epoch.book_count, 1,
                u"There should only be parent in common tag's counter."
            )

    def test_book_change_child(self):
        second_child_info = BookInfoStub(
            genre='X-Genre',
            epoch='X-Epoch',
            kind='Other-Kind',
            author=PersonStub(("Joe",), "Doe"),
            **info_args("Second Child")
        )
        SECOND_CHILD_TEXT = """<utwor>
        <opowiadanie>
            <akap><begin id="m01" /><motyw id="m01">Kot</motyw>
                Ala ma kota<end id="m01" /></akap>
        </opowiadanie></utwor>
        """
        # Import a second child.
        second_child = models.Book.from_text_and_meta(
            ContentFile(SECOND_CHILD_TEXT), second_child_info)
        # The book has only this new child now.
        self.book_info.parts = [second_child_info.url]
        self.book = models.Book.from_text_and_meta(
            ContentFile(self.BOOK_TEXT), self.book_info, overwrite=True)

        self.assertEqual(
                set(self.client.get('/katalog/gatunek/x-genre/'
                    ).context['object_list']),
                set([self.parent, self.child]),
                u"There should be parent and old child on common tag page."
            )
        kot = models.Tag.objects.get(slug='kot')
        self.assertEqual(self.parent.theme_counter, {kot.pk: 1},
                u"There should only be new child themes in parent theme counter."
            )
        epoch = models.Tag.objects.get(slug='x-epoch')
        self.assertEqual(epoch.book_count, 2,
                u"There should be parent and old child in common tag's counter."
            )
        self.assertEqual(
                list(self.client.get('/katalog/lektura/parent/motyw/kot/'
                    ).context['fragments']),
                [second_child.fragments.all()[0]],
                u"There should be new child's fragments on parent's theme page."
            )
        self.assertEqual(
                list(self.client.get('/katalog/lektura/parent/motyw/pies/'
                    ).context['fragments']),
                [],
                u"There should be no old child's fragments on parent's theme page."
            )


class MultilingualBookImportTest(WLTestCase):
    def setUp(self):
        WLTestCase.setUp(self)
        common_uri = WLURI.from_slug('common-slug')

        self.pol_info = BookInfoStub(
            genre='X-Genre',
            epoch='X-Epoch',
            kind='X-Kind',
            author=PersonStub(("Joe",), "Doe"),
            variant_of=common_uri,
            **info_args(u"Książka")
        )

        self.eng_info = BookInfoStub(
            genre='X-Genre',
            epoch='X-Epoch',
            kind='X-Kind',
            author=PersonStub(("Joe",), "Doe"),
            variant_of=common_uri,
            **info_args("A book", "eng")
        )

    def test_multilingual_import(self):
        BOOK_TEXT = """<utwor><opowiadanie><akap>A</akap></opowiadanie></utwor>"""

        book1 = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.pol_info)
        book2 = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.eng_info)

        self.assertEqual(
                set([b.language for b in models.Book.objects.all()]),
                set(['pol', 'eng']),
                'Books imported in wrong languages.'
            )


class BookImportGenerateTest(WLTestCase):
    def setUp(self):
        WLTestCase.setUp(self)
        xml = path.join(path.dirname(__file__), 'files/fraszka-do-anusie.xml')
        self.book = models.Book.from_xml_file(xml)

    def test_gen_pdf(self):
        self.book.pdf_file.build()
        book = models.Book.objects.get(pk=self.book.pk)
        self.assertTrue(path.exists(book.pdf_file.path))

    def test_gen_pdf_parent(self):
        """This book contains a child."""
        xml = path.join(path.dirname(__file__), "files/fraszki.xml")
        parent = models.Book.from_xml_file(xml)
        parent.pdf_file.build()
        parent = models.Book.objects.get(pk=parent.pk)
        self.assertTrue(path.exists(parent.pdf_file.path))

    def test_custom_pdf(self):
        from catalogue.tasks import build_custom_pdf
        from catalogue.utils import get_dynamic_path
        out = get_dynamic_path(None, 'test-custom', ext='pdf')
        absoulute_path = path.join(settings.MEDIA_ROOT, out)

        if not path.exists(path.dirname(absoulute_path)):
            makedirs(path.dirname(absoulute_path))

        build_custom_pdf(self.book.id,
            customizations=['nofootnotes', '13pt', 'a4paper'], file_name=out)
        self.assertTrue(path.exists(absoulute_path))
