# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def refresh_books(apps, schema_editor):
    Book = apps.get_model('catalogue', 'Book')
    TagRelation = apps.get_model('catalogue', 'TagRelation')
    db_alias = schema_editor.connection.alias
    for book in Book.objects.using(db_alias).all():
        book.cached_author = ', '.join(
            TagRelation.objects.filter(content_type__model='book', object_id=book.id, tag__category='author')
            .values_list('tag__name', flat=True))
        book.has_audience = 'audience' in book.extra_info
        book.save()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0015_book_recommended'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cached_author',
            field=models.CharField(db_index=True, max_length=240, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='has_audience',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(refresh_books, migrations.RunPython.noop),
    ]
