# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from .models import Tag, Book
from os.path import getmtime
import cPickle
from collections import defaultdict


BOOK_CATEGORIES = ('author', 'epoch', 'genre', 'kind')

_COUNTERS = None
_COUNTER_TIME = None


def get_top_level_related_tags(tags, categories=None):
    """
    Finds tags related to given tags through books, and counts their usage.

    Takes ancestry into account: if a tag is applied to a book, its
    usage on the book's descendants is ignored.
    """
    global _COUNTERS, _COUNTER_TIME
    # First, check that we have a valid and recent version of the counters.
    if getmtime(settings.CATALOGUE_COUNTERS_FILE) > _COUNTER_TIME:
        with open(settings.CATALOGUE_COUNTERS_FILE) as f:
            _COUNTERS = cPickle.load(f)

    tagids = tuple(sorted(t.pk for t in tags))
    try:
        related_ids = _COUNTERS['next'][tagids]
    except KeyError:
        return

    related = Tag.objects.filter(pk__in=related_ids)

    # TODO: do we really need that?
    if categories is not None:
        related = related.filter(category__in=categories)

    for tag in related:
        tag.count = _COUNTERS['count'][tuple(sorted(tagids + (tag.pk,)))]
        yield tag


def update_counters():
    def combinations(things):
        if len(things):
            for c in combinations(things[1:]):
                yield c
                yield (things[0],) + c
        else:
            yield ()

    def count_for_book(book, count_by_combination=None, parent_combinations=None):
        if not parent_combinations:
            parent_combinations = set()
        tags = sorted(book.tags.filter(category__in=('author', 'genre', 'epoch', 'kind')).values_list('pk', flat=True))
        combs = list(combinations(tags))
        for c in combs:
            if c not in parent_combinations:
                count_by_combination[c] += 1
        combs_for_child = set(list(parent_combinations) + combs)
        for child in book.children.all():
            count_for_book(child, count_by_combination, combs_for_child)

    count_by_combination = defaultdict(lambda: 0)
    for b in Book.objects.filter(parent=None):
        count_for_book(b, count_by_combination)

    next_combinations = defaultdict(set)
    # Now build an index of all combinations.
    for c in count_by_combination.keys():
        if not c:
            continue
        for n in c:
            rest = tuple(x for x in c if x != n)
            next_combinations[rest].add(n)

    counters = {
        "count": dict(count_by_combination),
        "next": dict(next_combinations),
    }

    with open(settings.CATALOGUE_COUNTERS_FILE, 'w') as f:
        cPickle.dump(counters, f)
