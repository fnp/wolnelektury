# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdcounter', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookstub',
            options={'ordering': ('title',), 'verbose_name': 'book stub', 'verbose_name_plural': 'book stubs'},
        ),
        migrations.AlterField(
            model_name='author',
            name='death',
            field=models.IntegerField(null=True, verbose_name='year of death', blank=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='description',
            field=models.TextField(verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='slug',
            field=models.SlugField(unique=True, max_length=120, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='author',
            name='sort_key',
            field=models.CharField(max_length=120, verbose_name='sort key', db_index=True),
        ),
        migrations.AlterField(
            model_name='bookstub',
            name='pd',
            field=models.IntegerField(null=True, verbose_name='goes to public domain', blank=True),
        ),
        migrations.AlterField(
            model_name='bookstub',
            name='slug',
            field=models.SlugField(unique=True, max_length=120, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='bookstub',
            name='title',
            field=models.CharField(max_length=120, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='bookstub',
            name='translator',
            field=models.TextField(verbose_name='translator', blank=True),
        ),
    ]
