# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('push', '0002_auto_20180830_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='image',
            field=models.ImageField(upload_to='push/img', verbose_name='image', blank=True),
        ),
    ]
