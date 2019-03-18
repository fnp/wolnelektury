# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0017_auto_20171214_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmedia',
            name='part_name',
            field=models.CharField(default='', max_length=512, verbose_name='part name', blank=True),
        ),
    ]
