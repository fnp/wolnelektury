# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from jsonfield import JSONField


class ISBNPool(models.Model):
    prefix = models.CharField(max_length=10)
    suffix_from = models.IntegerField()
    suffix_to = models.IntegerField()
    ref_from = models.IntegerField()
    next_suffix = models.IntegerField()

    @staticmethod
    def check_digit(prefix12):
        digits = [int(d) for d in prefix12]
        return str((-sum(digits[0::2]) + 7 * sum(digits[1::2])) % 10)

    def isbn(self, suffix):
        prefix_length = len(self.prefix)
        suffix_length = 12 - prefix_length
        suffix_str = ('%%0%dd' % suffix_length) % suffix
        prefix12 = self.prefix + suffix_str
        return prefix12 + self.check_digit(prefix12)


class ONIXRecord(models.Model):
    isbn_pool = models.ForeignKey(ISBNPool)
    datestamp = models.DateField(auto_now=True)
    suffix = models.IntegerField()
    product_form = models.CharField(max_length=4)
    product_form_detail = models.CharField(max_length=8, blank=True)
    title = models.CharField(max_length=256)
    part_number = models.CharField(max_length=64, blank=True)
    contributors = JSONField()  # roles, names, optional: ISNI, date of birth/death
    edition_type = models.CharField(max_length=4)
    edition_number = models.IntegerField(default=1)
    language = models.CharField(max_length=4)
    imprint = models.CharField(max_length=256)
    publishing_date = models.DateField()

    class Meta:
        ordering = ['isbn_pool__id', 'suffix']

    def isbn(self):
        return self.isbn_pool.isbn(self.suffix)

    def reference(self):
        return 'pl-eisbn-%s' % (self.isbn_pool.ref_from + self.suffix)
