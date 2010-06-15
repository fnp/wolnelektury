# -*- coding: utf-8 -*-
from catalogue import models, views
from catalogue.test_utils import *

from nose.tools import raises

class BasicSearchLogicTests(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
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
