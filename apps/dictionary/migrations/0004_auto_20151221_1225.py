# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_auto_20141023_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='qualifiers',
            field=models.ManyToManyField(to='dictionary.Qualifier'),
        ),
    ]
