# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funding', '0002_auto_20151221_1225'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='funding',
            options={'ordering': ['-payed_at', 'pk'], 'verbose_name': 'funding', 'verbose_name_plural': 'fundings'},
        ),
    ]
