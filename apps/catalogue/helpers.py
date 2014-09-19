# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from .models import Tag, Book


BOOK_CATEGORIES = ('author', 'epoch', 'genre', 'kind')


def get_top_level_related_tags(tags=None, categories=BOOK_CATEGORIES):
    """
    Finds tags related to given tags through books, and counts their usage.

    Takes ancestry into account: if a tag is applied to a book, its
    usage on the book's descendants is ignored.

    This is tested for PostgreSQL 9.1+, and might not work elsewhere.
    It particular, it uses raw SQL using WITH clause, which is
    supported in SQLite from v. 3.8.3, and is missing in MySQL.
    http://bugs.mysql.com/bug.php?id=16244

    """
    # First, find all tag relations of relevant books.
    bct = ContentType.objects.get_for_model(Book)
    relations = Tag.intermediary_table_model.objects.filter(
        content_type=bct)
    if tags is not None:
        tagged_books = Book.tagged.with_all(tags).only('pk')
        relations = relations.filter(
            object_id__in=tagged_books).exclude(
            tag_id__in=[tag.pk for tag in tags])

    rel_sql, rel_params = relations.query.sql_with_params()

    # Exclude those relations between a book and a tag,
    # for which there is a relation between the book's ancestor
    # and the tag and 

    return Tag.objects.raw('''
        WITH AllTagged AS (''' + rel_sql + ''')
        SELECT catalogue_tag.*, COUNT(catalogue_tag.id) AS count
        FROM catalogue_tag, AllTagged
        WHERE catalogue_tag.id=AllTagged.tag_id
            AND catalogue_tag.category IN %s
            AND NOT EXISTS (
                SELECT AncestorTagged.id
                FROM catalogue_book_ancestor Ancestor,
                    AllTagged AncestorTagged
                WHERE Ancestor.from_book_id=AllTagged.object_id
                    AND AncestorTagged.content_type_id=%s
                    AND AncestorTagged.object_id=Ancestor.to_book_id
                    AND AncestorTagged.tag_id=AllTagged.tag_id
            )
        GROUP BY catalogue_tag.id
        ORDER BY sort_key''', rel_params + (categories, bct.pk))
