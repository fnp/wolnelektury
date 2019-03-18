# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isbn', '0003_isbnpool_purpose'),
    ]

    operations = [
        migrations.AddField(
            model_name='onixrecord',
            name='dc_slug',
            field=models.CharField(default='', max_length=256, db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='onixrecord',
            unique_together=set([('isbn_pool', 'suffix')]),
        ),
    ]
