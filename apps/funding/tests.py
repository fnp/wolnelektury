# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.test import TestCase
from .models import Offer, Perk, Funding


class FundTest(TestCase):
    def setUp(self):
        self.offer1 = Offer.objects.create(
            author='author1', title='title1', slug='slug1',
            target=100, start='2013-03-01', end='2013-03-31')

    def test_perks(self):
        perk = Perk.objects.create(price=20, name='Perk 20')
        perk1 = Perk.objects.create(offer=self.offer1, price=50, name='Perk 50')
        offer2 = Offer.objects.create(
            author='author2', title='title2', slug='slug2',
            target=100, start='2013-02-01', end='2013-02-20')
        perk2 = Perk.objects.create(offer=offer2, price=1, name='Perk 1')

        self.assertEqual(
            set(self.offer1.fund('Tester', 'test@example.com', 10).perks.all()),
            set())
        self.assertEqual(
            set(self.offer1.fund('Tester', 'test@example.com', 70).perks.all()),
            set([perk, perk1]))
