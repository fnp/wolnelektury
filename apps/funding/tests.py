# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import date, timedelta
from django.test import TestCase
from .models import Offer, Perk, Funding


class PerksTest(TestCase):
    def setUp(self):
        self.today = date.today()
        self.offer1 = Offer.objects.create(
            author='author1', title='title1', slug='slug1',
            target=100, start=self.today, end=self.today)

    def test_perks(self):
        perk = Perk.objects.create(price=20, name='Perk 20')
        perk1 = Perk.objects.create(offer=self.offer1, price=50, name='Perk 50')
        offer2 = Offer.objects.create(
            author='author2', title='title2', slug='slug2',
            target=100, start=self.today-timedelta(1), end=self.today-timedelta(1))
        perk2 = Perk.objects.create(offer=offer2, price=1, name='Perk 1')

        self.assertEqual(
            set(self.offer1.get_perks(10)),
            set())
        self.assertEqual(
            set(self.offer1.get_perks(70)),
            set([perk, perk1]))


class FundingTest(TestCase):
    def setUp(self):
        self.today = date.today()
        self.offer_past = Offer.objects.create(
            author='an-author', title='past', slug='past',
            target=100, start=self.today-timedelta(1), end=self.today-timedelta(1))
        self.offer_current = Offer.objects.create(
            author='an-author', title='current', slug='current',
            target=100, start=self.today, end=self.today)
        self.offer_future = Offer.objects.create(
            author='an-author', title='future', slug='future',
            target=100, start=self.today+timedelta(1), end=self.today+timedelta(1))

    def test_current(self):
        self.assertTrue(self.offer_current.is_current())
        self.assertFalse(self.offer_past.is_current())
        self.assertEqual(Offer.current(), self.offer_current)
        self.assertEqual(
            set(Offer.past()),
            set([self.offer_past])
        )
        self.assertEqual(
            set(Offer.public()),
            set([self.offer_past, self.offer_current])
        )

    def test_interrupt(self):
        # A new offer starts, ending the previously current one.
        offer_interrupt = Offer.objects.create(
            author='an-author', title='interrupt', slug='interrupt',
            target=100, start=self.today-timedelta(1), end=self.today+timedelta(1))

        self.assertTrue(offer_interrupt.is_current())
        self.assertFalse(self.offer_current.is_current())
        self.assertEqual(Offer.current(), offer_interrupt)
        self.assertEqual(
            set(Offer.past()),
            set([self.offer_past, self.offer_current])
        )
        self.assertEqual(
            set(Offer.public()),
            set([self.offer_past, self.offer_current, offer_interrupt])
        )

