# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_populate_ancestors'),
    ]

    operations = [
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
