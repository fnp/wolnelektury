# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_auto_20141022_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=120, verbose_name='name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name_de',
            field=models.CharField(max_length=120, null=True, verbose_name='name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name_en',
            field=models.CharField(max_length=120, null=True, verbose_name='name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name_es',
            field=models.CharField(max_length=120, null=True, verbose_name='name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name_fr',
            field=models.CharField(max_length=120, null=True, verbose_name='name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name_it',
            field=models.CharField(max_length=120, null=True, verbose_name='name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name_lt',
            field=models.CharField(max_length=120, null=True, verbose_name='name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name_pl',
            field=models.CharField(max_length=120, null=True, verbose_name='name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name_ru',
            field=models.CharField(max_length=120, null=True, verbose_name='name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name_uk',
            field=models.CharField(max_length=120, null=True, verbose_name='name', db_index=True),
            preserve_default=True,
        ),
    ]
