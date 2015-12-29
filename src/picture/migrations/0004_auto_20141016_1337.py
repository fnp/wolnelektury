# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0003_auto_20140924_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='title',
            field=models.CharField(max_length=32767, verbose_name='Title'),
        ),
    ]
