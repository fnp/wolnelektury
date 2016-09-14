# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'subscription', 'verbose_name_plural': 'subscriptions'},
        ),
        migrations.AlterField(
            model_name='subscription',
            name='active',
            field=models.BooleanField(default=True, verbose_name='active'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='email',
            field=models.EmailField(unique=True, max_length=254, verbose_name='email address'),
        ),
    ]
