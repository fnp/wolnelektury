# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.sites.models import Site
from django.utils.functional import lazy
from catalogue.models import Book, Tag


WL_BASE = lazy(
    lambda: 'https://' + Site.objects.get_current().domain, str)()

category_singular = {
    'authors': 'author',
    'kinds': 'kind',
    'genres': 'genre',
    'epochs': 'epoch',
    'themes': 'theme',
    'books': 'book',
}


def read_tags(tags, request, allowed):
    """ Reads a path of filtering tags.

    :param str tags: a path of category and slug pairs, like: authors/an-author/...
    :returns: list of Tag objects
    :raises: ValueError when tags can't be found
    """

    def process(category, slug):
        if category == 'book':
            # FIXME: Unused?
            try:
                books.append(Book.objects.get(slug=slug))
            except Book.DoesNotExist:
                raise ValueError('Unknown book.')
        try:
            real_tags.append(Tag.objects.get(category=category, slug=slug))
        except Tag.DoesNotExist:
            raise ValueError('Tag not found')

    if not tags:
        return [], []

    tags = tags.strip('/').split('/')
    real_tags = []
    books = []
    while tags:
        category = tags.pop(0)
        slug = tags.pop(0)

        try:
            category = category_singular[category]
        except KeyError:
            raise ValueError('Unknown category.')

        if category not in allowed:
            raise ValueError('Category not allowed.')
        process(category, slug)

    for key in request.GET:
        if key in category_singular:
            category = category_singular[key]
            if category in allowed:
                for slug in request.GET.getlist(key):
                    process(category, slug)
    return real_tags, books
