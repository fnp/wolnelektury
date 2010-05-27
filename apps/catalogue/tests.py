# -*- coding: utf-8 -*-
from django.test import TestCase
from catalogue import models, views
from django.contrib.auth.models import User, AnonymousUser

class SimpleSearchTest(TestCase):
    def setUp(self):
        t = models.Tag(name=u'Tadeusz Żeleński (Boy)', category=u'author', slug=u'a1')
        t.save()
        self.t = t
        self.user = AnonymousUser()
    
    def tearDown(self):
        self.t.delete()
    
    def test_too_short(self):
        self.assertRaises(ValueError, views.find_best_matches, u'', self.user)
        self.assertRaises(ValueError, views.find_best_matches, u't', self.user)
        
    def test_match_beginning(self):
        self.assertEqual(views.find_best_matches(u'Tad', self.user), (self.t,))
    
    def test_match_case(self):
        self.assertEqual(views.find_best_matches(u'TAD', self.user), (self.t,))

    def test_word_boundary(self):
        self.assertEqual(views.find_best_matches(u'Boy', self.user), (self.t,))
        self.assertEqual(views.find_best_matches(u'(Boy', self.user), (self.t,))

    def test_not_found(self):
        self.assertEqual(views.find_best_matches(u'andrzej', self.user), ())
        self.assertEqual(views.find_best_matches(u'deusz', self.user), ())
    
    def test_locale(self):
        self.assertEqual(views.find_best_matches(u'ele', self.user), ())
        self.assertEqual(views.find_best_matches(u'Żele', self.user), (self.t,))
        self.assertEqual(views.find_best_matches(u'żele', self.user), (self.t,))
    
    def test_sloppy(self):
        self.assertEqual(views.find_best_matches(u'Żelenski', self.user), (self.t,))
        self.assertEqual(views.find_best_matches(u'zelenski', self.user), (self.t,))
        


class SetSearchTest(TestCase):
    def setUp(self):
        self.me = User(name='me')
        self.other = User(name='other')
    
    def tearDown(self):
        self.me.delete()
        self.other.delete()
    
