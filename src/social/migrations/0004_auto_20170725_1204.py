# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0003_cite_banner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cite',
            name='text',
            field=models.TextField(verbose_name='text', blank=True),
        ),
    ]
