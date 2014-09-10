# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def fix_tree_tags(apps, schema_editor):
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
        for b in Book.objects.exclude(parent=None):
            parent = b.parent
            while parent is not None:
                b.ancestor.add(parent)
                parent = parent.parent


def remove_book_tags(apps, schema_editor):
    Tag = apps.get_model("catalogue", "Tag")
    Book = apps.get_model("catalogue", "Book")
    Tag.objects.filter(category='book').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='ancestor',
            field=models.ManyToManyField(related_name=b'descendant', null=True, editable=False, to='catalogue.Book', blank=True),
            preserve_default=True,
        ),

        migrations.RunPython(fix_tree_tags),
        migrations.RunPython(remove_book_tags),

        migrations.AlterField(
            model_name='tag',
            name='category',
            field=models.CharField(db_index=True, max_length=50, verbose_name='Category', choices=[(b'author', 'author'), (b'epoch', 'period'), (b'kind', 'form'), (b'genre', 'genre'), (b'theme', 'motif'), (b'set', 'set'), (b'thing', 'thing')]),
        ),

        migrations.RemoveField(
            model_name='tag',
            name='book_count',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='picture_count',
        ),
        migrations.RemoveField(
            model_name='book',
            name='_related_info',
        ),
    ]
