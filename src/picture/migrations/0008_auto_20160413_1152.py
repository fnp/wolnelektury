# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0007_auto_20160125_1709'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='picture',
            options={'ordering': ('sort_key_author', 'sort_key'), 'verbose_name': 'picture', 'verbose_name_plural': 'pictures'},
        ),
    ]
