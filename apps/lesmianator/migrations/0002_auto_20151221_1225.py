# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lesmianator', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poem',
            name='created_from',
            field=jsonfield.fields.JSONField(null=True, verbose_name='extra information', blank=True),
        ),
        migrations.AlterField(
            model_name='poem',
            name='slug',
            field=models.SlugField(max_length=120, verbose_name='slug'),
        ),
    ]
