# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chunks', '0002_auto_20140911_1253'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chunk',
            options={'ordering': ('key',), 'verbose_name': 'chunk', 'verbose_name_plural': 'chunks'},
        ),
        migrations.AlterField(
            model_name='chunk',
            name='description',
            field=models.CharField(max_length=255, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='key',
            field=models.CharField(help_text='A unique name for this chunk of content', max_length=255, serialize=False, verbose_name='key', primary_key=True),
        ),
    ]
