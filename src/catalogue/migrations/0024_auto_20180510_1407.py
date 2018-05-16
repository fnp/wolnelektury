# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0023_book_abstract'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='preview',
            field=models.BooleanField(default=False, verbose_name='preview'),
        ),
        migrations.AddField(
            model_name='book',
            name='preview_until',
            field=models.DateField(null=True, verbose_name='preview until', blank=True),
        ),
    ]
