# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-16 08:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0003_remove_payuorder_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='payucardtoken',
            name='pos_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]