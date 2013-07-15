# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import date, timedelta
from django.test import TestCase
from .models import Offer, Perk, Funding


class FundTest(TestCase):
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
