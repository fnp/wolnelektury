# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0005_auto_20141022_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='extra_info',
            field=jsonfield.fields.JSONField(default={}, verbose_name='extra information'),
        ),
        migrations.AlterField(
            model_name='picture',
            name='slug',
            field=models.SlugField(unique=True, max_length=120, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='picture',
            name='sort_key',
            field=models.CharField(verbose_name='sort key', max_length=120, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='picture',
            name='title',
            field=models.CharField(max_length=32767, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='picturearea',
            name='kind',
            field=models.CharField(db_index=True, max_length=10, verbose_name='kind', choices=[(b'thing', 'thing'), (b'theme', 'theme')]),
        ),
    ]
