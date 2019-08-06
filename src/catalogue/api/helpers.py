# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db.models import Q
from catalogue.models import Book


def books_after(books, after, new_api):
    if not new_api:
        return books.filter(slug__gt=after)
    try:
        author, title, book_id = after.split(Book.SORT_KEY_SEP)
    except ValueError:
        return Book.objects.none()
    return books.filter(Q(sort_key_author__gt=author)
                        | (Q(sort_key_author=author) & Q(sort_key__gt=title))
                        | (Q(sort_key_author=author) & Q(sort_key=title) & Q(id__gt=int(book_id))))


def order_books(books, new_api):
    if new_api:
        return books.order_by('sort_key_author', 'sort_key', 'id')
    else:
        return books.order_by('slug')

