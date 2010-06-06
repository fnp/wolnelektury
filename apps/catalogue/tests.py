# -*- coding: utf-8 -*-
from django.test import TestCase
from catalogue import models, views
from django.core.files.base import ContentFile
from django.contrib.auth.models import User, AnonymousUser

from nose.tools import raises
from StringIO import StringIO

class BasicSearchLogicTests(TestCase):

    def setUp(self):
        self.author_tag = models.Tag.objects.create(
                                name=u'Adam Mickiewicz [SubWord]',
                                category=u'author', slug="one")

        self.unicode_tag = models.Tag.objects.create(
                                name=u'Tadeusz Żeleński (Boy)',
                                category=u'author', slug="two")

        self.polish_tag = models.Tag.objects.create(
                                name=u'ĘÓĄŚŁŻŹĆŃęóąśłżźćń',
                                category=u'author', slug="three")

    @raises(ValueError)
    def test_empty_query(self):
        """ Check that empty queries raise an error. """
        views.find_best_matches(u'')

    @raises(ValueError)
    def test_one_letter_query(self):
        """ Check that one letter queries aren't permitted. """
        views.find_best_matches(u't')

    def test_match_by_prefix(self):
        """ Tags should be matched by prefix of words within it's name. """
        self.assertEqual(views.find_best_matches(u'Ada'), (self.author_tag,))
        self.assertEqual(views.find_best_matches(u'Mic'), (self.author_tag,))
        self.assertEqual(views.find_best_matches(u'Mickiewicz'), (self.author_tag,))

    def test_match_case_insensitive(self):
        """ Tag names should match case insensitive. """
        self.assertEqual(views.find_best_matches(u'adam mickiewicz'), (self.author_tag,))

    def test_match_case_insensitive_unicode(self):
        """ Tag names should match case insensitive (unicode). """
        self.assertEqual(views.find_best_matches(u'tadeusz żeleński (boy)'), (self.unicode_tag,))

    def test_word_boundary(self):
        self.assertEqual(views.find_best_matches(u'SubWord'), (self.author_tag,))
        self.assertEqual(views.find_best_matches(u'[SubWord'), (self.author_tag,))

    def test_unrelated_search(self):
        self.assertEqual(views.find_best_matches(u'alamakota'), tuple())
        self.assertEqual(views.find_best_matches(u'Adama'), ())

    def test_infix_doesnt_match(self):
        """ Searching for middle of a word shouldn't match. """
        self.assertEqual(views.find_best_matches(u'deusz'), tuple())

    def test_diactricts_removal_pl(self):
        """ Tags should match both with and without national characters. """
        self.assertEqual(views.find_best_matches(u'ĘÓĄŚŁŻŹĆŃęóąśłżźćń'), (self.polish_tag,))
        self.assertEqual(views.find_best_matches(u'EOASLZZCNeoaslzzcn'), (self.polish_tag,))
        self.assertEqual(views.find_best_matches(u'eoaslzzcneoaslzzcn'), (self.polish_tag,))

    def test_diactricts_query_removal_pl(self):
        """ Tags without national characters shouldn't be matched by queries with them. """
        self.assertEqual(views.find_best_matches(u'Adąm'), ())

    def test_sloppy(self):
        self.assertEqual(views.find_best_matches(u'Żelenski'), (self.unicode_tag,))
        self.assertEqual(views.find_best_matches(u'zelenski'), (self.unicode_tag,))


class PersonStub(object):

    def __init__(self, first_names, last_name):
        self.first_names = first_names
        self.last_name = last_name

class BookInfoStub(object):

    def __init__(self, **kwargs):
        self.__dict = kwargs

    def __setattr__(self, key, value):
        if not key.startswith('_'):
            self.__dict[key] = value
        return object.__setattr__(self, key, value)

    def __getattr__(self, key):
        return self.__dict[key]

    def to_dict(self):
        return dict((key, unicode(value)) for key, value in self.__dict.items())

class BookImportLogicTests(TestCase):

    def setUp(self):
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
           ('book', 'l-default_book'),
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
        self.assertTrue(book.has_html_file())

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

    def test_book_with_fragment(self):
        BOOK_TEXT = """<utwor>
        <opowiadanie>
            <akap><begin id="m01" /><motyw id="m01">Love</motyw>Ala ma kota<end id="m01" /></akap>
        </opowiadanie></utwor>
        """

        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

        self.assertEqual(book.fragments.count(), 1)
        self.assertEqual(book.fragments.all()[0].text, u'<p class="paragraph">Ala ma kota</p>\n')

        self.assert_(('theme', 'love') in [ (tag.category, tag.slug) for tag in book.tags ])

    def test_book_replace_title(self):
        BOOK_TEXT = """<utwor />"""
        self.book_info.title = u"Extraordinary"
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

        tags = [ (tag.category, tag.slug) for tag in book.tags ]
        tags.sort()

        self.assertEqual(tags, self.expected_tags)

    def test_book_replace_author(self):
        BOOK_TEXT = """<utwor />"""
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


