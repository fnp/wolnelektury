# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cite',
            name='image_title',
            field=models.CharField(max_length=255, null=True, verbose_name='title', blank=True),
        ),
    ]
