# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-26 08:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0025_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='preview_key',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]