# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-17 13:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0007_auto_20190416_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
