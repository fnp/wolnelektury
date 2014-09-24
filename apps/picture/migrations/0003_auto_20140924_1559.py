# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0002_remove_picture__related_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Title'),
        ),
    ]
