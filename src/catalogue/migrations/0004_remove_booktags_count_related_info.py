# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_populate_ancestors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='category',
            field=models.CharField(db_index=True, max_length=50, verbose_name='Category', choices=[('author', 'author'), ('epoch', 'period'), ('kind', 'form'), ('genre', 'genre'), ('theme', 'motif'), ('set', 'set'), ('thing', 'thing')]),
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
