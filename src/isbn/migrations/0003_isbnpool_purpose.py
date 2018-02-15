# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isbn', '0002_auto_20180213_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='isbnpool',
            name='purpose',
            field=models.CharField(default='', max_length=4, choices=[(b'WL', b'Wolne Lektury'), (b'FNP', b'Fundacja Nowoczesna Polska')]),
            preserve_default=False,
        ),
    ]
