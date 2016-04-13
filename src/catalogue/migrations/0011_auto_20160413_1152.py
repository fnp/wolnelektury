# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_bookpopularity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ('sort_key_author', 'sort_key'), 'verbose_name': 'book', 'verbose_name_plural': 'books'},
        ),
    ]
