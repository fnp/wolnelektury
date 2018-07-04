# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paypal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingagreement',
            name='token',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]
