# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infopages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infopage',
            name='slug',
            field=models.SlugField(unique=True, max_length=120, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='infopage',
            name='title',
            field=models.CharField(max_length=120, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='infopage',
            name='title_de',
            field=models.CharField(max_length=120, null=True, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='infopage',
            name='title_en',
            field=models.CharField(max_length=120, null=True, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='infopage',
            name='title_es',
            field=models.CharField(max_length=120, null=True, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='infopage',
            name='title_fr',
            field=models.CharField(max_length=120, null=True, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='infopage',
            name='title_it',
            field=models.CharField(max_length=120, null=True, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='infopage',
            name='title_lt',
            field=models.CharField(max_length=120, null=True, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='infopage',
            name='title_pl',
            field=models.CharField(max_length=120, null=True, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='infopage',
            name='title_ru',
            field=models.CharField(max_length=120, null=True, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='infopage',
            name='title_uk',
            field=models.CharField(max_length=120, null=True, verbose_name='title', blank=True),
        ),
    ]
