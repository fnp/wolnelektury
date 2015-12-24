# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deleted',
            name='slug',
            field=models.SlugField(max_length=120, verbose_name='slug', blank=True),
        ),
    ]
