# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.db.models import F


class ISBNPool(models.Model):
    PURPOSE_WL = 'WL'
    PURPOSE_FNP = 'FNP'
    PURPOSE_CHOICES = (
        (PURPOSE_WL, 'Wolne Lektury'),
        (PURPOSE_FNP, 'Fundacja Nowoczesna Polska'),
    )

    prefix = models.CharField(max_length=10)
    suffix_from = models.IntegerField()
    suffix_to = models.IntegerField()
    ref_from = models.IntegerField()
    next_suffix = models.IntegerField()
    purpose = models.CharField(max_length=4, choices=PURPOSE_CHOICES)

    def __str__(self):
        return self.prefix

    @classmethod
    def active_pool(cls, purpose):
        pools = cls.objects.filter(purpose=purpose)
        pools = pools.exclude(next_suffix__gt=F('suffix_to'))
        if len(pools) == 1:
            return pools.get()
        else:
            pools.exclude(next_suffix=F('suffix_from'))
            return pools.get()

    @staticmethod
    def check_digit(prefix12):
        digits = [int(d) for d in prefix12]
        return str((-sum(digits[0::2]) + 7 * sum(digits[1::2])) % 10)

    def isbn(self, suffix, dashes=False):
        prefix_length = len(self.prefix)
        suffix_length = 12 - prefix_length
        suffix_str = ('%%0%dd' % suffix_length) % suffix
        prefix12 = self.prefix + suffix_str
        if dashes:
            prefix12_final = '%s-%s-%s-%s-' % (self.prefix[:3], self.prefix[3:5], self.prefix[5:], suffix_str)
        else:
            prefix12_final = prefix12
        return prefix12_final + self.check_digit(prefix12)


class ONIXRecord(models.Model):
    isbn_pool = models.ForeignKey(ISBNPool, models.PROTECT)
    datestamp = models.DateField(auto_now=True)
    suffix = models.IntegerField()
    product_form = models.CharField(max_length=4)
    product_form_detail = models.CharField(max_length=8, blank=True)
    title = models.CharField(max_length=256)
    part_number = models.CharField(max_length=64, blank=True)
    contributors = models.TextField()  # roles, names, optional: ISNI, date of birth/death
    edition_type = models.CharField(max_length=4)
    edition_number = models.IntegerField(default=1)
    language = models.CharField(max_length=4)
    imprint = models.CharField(max_length=256)
    publishing_date = models.DateField()
    dc_slug = models.CharField(max_length=256, default='', db_index=True)

    class Meta:
        ordering = ['isbn_pool__id', 'suffix']
        unique_together = ['isbn_pool', 'suffix']

    @classmethod
    def new_record(cls, purpose, data):
        pool = ISBNPool.active_pool(purpose)
        fields = {
            'isbn_pool': pool,
            'suffix': pool.next_suffix,
        }
        fields_to_copy = [
            'product_form',
            'product_form_detail',
            'title',
            'part_number',
            'contributors',  # ???
            'edition_type',
            'edition_number',
            'language',
            'imprint',
            'publishing_date',
            'dc_slug',
        ]
        for field in fields_to_copy:
            if field in data:
                fields[field] = data[field]
        cls.objects.create(**fields)
        pool.next_suffix += 1
        pool.save()

    def isbn(self, dashes=False):
        return self.isbn_pool.isbn(self.suffix, dashes=dashes)

    def reference(self):
        return 'pl-eisbn-%s' % (self.isbn_pool.ref_from + self.suffix)
