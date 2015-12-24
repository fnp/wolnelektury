# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funding', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funding',
            name='email',
            field=models.EmailField(db_index=True, max_length=254, verbose_name='email', blank=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='description',
            field=models.TextField(verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='slug',
            field=models.SlugField(verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='title',
            field=models.CharField(max_length=255, verbose_name='title'),
        ),
    ]
