# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from .models import Tag, Book
from os.path import getmtime
import pickle
from collections import defaultdict


BOOK_CATEGORIES = ('author', 'epoch', 'genre', 'kind')

_COUNTERS = None
_COUNTER_TIME = 0


def get_top_level_related_tags(tags, categories=None):
    """
    Finds tags related to given tags through books, and counts their usage.

    Takes ancestry into account: if a tag is applied to a book, its
    usage on the book's descendants is ignored.
    """
    global _COUNTERS, _COUNTER_TIME
    # First, check that we have a valid and recent version of the counters.
    if getmtime(settings.CATALOGUE_COUNTERS_FILE) > _COUNTER_TIME:
        for i in range(10):
            try:
                with open(settings.CATALOGUE_COUNTERS_FILE, 'rb') as f:
                    _COUNTERS = pickle.load(f)
            except (EOFError, ValueError):
                if i < 9:
                    continue
                else:
                    raise
            else:
                break

    tagids = tuple(sorted(t.pk for t in tags))
    try:
        related_ids = _COUNTERS['next'][tagids]
    except KeyError:
        return

    related = Tag.objects.filter(pk__in=related_ids)

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
    for b in Book.objects.filter(findable=True, parent=None):
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

    with open(settings.CATALOGUE_COUNTERS_FILE, 'wb') as f:
        pickle.dump(counters, f)


def get_audiobook_tags():
    audiobook_tag_ids = cache.get('audiobook_tags')
    if audiobook_tag_ids is None:
        books_with_audiobook = Book.objects.filter(findable=True, media__type__in=('mp3', 'ogg'))\
            .distinct().values_list('pk', flat=True)
        audiobook_tag_ids = Tag.objects.filter(
            items__content_type=ContentType.objects.get_for_model(Book),
            items__object_id__in=list(books_with_audiobook)).distinct().values_list('pk', flat=True)
        audiobook_tag_ids = list(audiobook_tag_ids)
        cache.set('audiobook_tags', audiobook_tag_ids)
    return audiobook_tag_ids
