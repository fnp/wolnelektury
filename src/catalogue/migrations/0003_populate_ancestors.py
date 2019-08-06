# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations


def populate_ancestors(apps, schema_editor):
    """Fixes the ancestry cache."""
    # TODO: table names
    from django.db import connection, transaction
    if connection.vendor == 'postgres':
        cursor = connection.cursor()
        cursor.execute("""
            WITH RECURSIVE ancestry AS (
                SELECT book.id, book.parent_id
                FROM catalogue_book AS book
                WHERE book.parent_id IS NOT NULL
                UNION
                SELECT ancestor.id, book.parent_id
                FROM ancestry AS ancestor, catalogue_book AS book
                WHERE ancestor.parent_id = book.id
                    AND book.parent_id IS NOT NULL
                )
            INSERT INTO catalogue_book_ancestor
                (from_book_id, to_book_id)
                SELECT id, parent_id
                FROM ancestry
                ORDER BY id;
            """)
    else:
        Book = apps.get_model("catalogue", "Book")
        for book in Book.objects.exclude(parent=None):
            parent = book.parent
            while parent is not None:
                book.ancestor.add(parent)
                parent = parent.parent


def remove_book_tags(apps, schema_editor):
    Tag = apps.get_model("catalogue", "Tag")
    Book = apps.get_model("catalogue", "Book")
    Tag.objects.filter(category='book').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0002_book_ancestor'),
    ]

    operations = [
        migrations.RunPython(populate_ancestors),
        migrations.RunPython(remove_book_tags),
    ]
