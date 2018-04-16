# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0022_auto_20180226_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='abstract',
            field=models.TextField(verbose_name='abstract', blank=True),
        ),
    ]
