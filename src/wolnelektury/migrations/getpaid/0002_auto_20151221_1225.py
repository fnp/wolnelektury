# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getpaid', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='description',
            field=models.CharField(max_length=128, null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(default=b'new', max_length=20, verbose_name='status', db_index=True, choices=[(b'new', 'new'), (b'in_progress', 'in progress'), (b'accepted_for_proc', 'accepted for processing'), (b'partially_paid', 'partially paid'), (b'paid', 'paid'), (b'cancelled', 'cancelled'), (b'failed', 'failed')]),
        ),
    ]
