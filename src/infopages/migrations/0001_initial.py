# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InfoPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('main_page', models.IntegerField(null=True, verbose_name='main page priority', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=120, verbose_name='Slug')),
                ('title', models.CharField(max_length=120, verbose_name='Title', blank=True)),
                ('title_de', models.CharField(max_length=120, null=True, verbose_name='Title', blank=True)),
                ('title_en', models.CharField(max_length=120, null=True, verbose_name='Title', blank=True)),
                ('title_es', models.CharField(max_length=120, null=True, verbose_name='Title', blank=True)),
                ('title_fr', models.CharField(max_length=120, null=True, verbose_name='Title', blank=True)),
                ('title_it', models.CharField(max_length=120, null=True, verbose_name='Title', blank=True)),
                ('title_lt', models.CharField(max_length=120, null=True, verbose_name='Title', blank=True)),
                ('title_pl', models.CharField(max_length=120, null=True, verbose_name='Title', blank=True)),
                ('title_ru', models.CharField(max_length=120, null=True, verbose_name='Title', blank=True)),
                ('title_uk', models.CharField(max_length=120, null=True, verbose_name='Title', blank=True)),
                ('left_column', models.TextField(verbose_name='left column', blank=True)),
                ('left_column_de', models.TextField(null=True, verbose_name='left column', blank=True)),
                ('left_column_en', models.TextField(null=True, verbose_name='left column', blank=True)),
                ('left_column_es', models.TextField(null=True, verbose_name='left column', blank=True)),
                ('left_column_fr', models.TextField(null=True, verbose_name='left column', blank=True)),
                ('left_column_it', models.TextField(null=True, verbose_name='left column', blank=True)),
                ('left_column_lt', models.TextField(null=True, verbose_name='left column', blank=True)),
                ('left_column_pl', models.TextField(null=True, verbose_name='left column', blank=True)),
                ('left_column_ru', models.TextField(null=True, verbose_name='left column', blank=True)),
                ('left_column_uk', models.TextField(null=True, verbose_name='left column', blank=True)),
                ('right_column', models.TextField(verbose_name='right column', blank=True)),
                ('right_column_de', models.TextField(null=True, verbose_name='right column', blank=True)),
                ('right_column_en', models.TextField(null=True, verbose_name='right column', blank=True)),
                ('right_column_es', models.TextField(null=True, verbose_name='right column', blank=True)),
                ('right_column_fr', models.TextField(null=True, verbose_name='right column', blank=True)),
                ('right_column_it', models.TextField(null=True, verbose_name='right column', blank=True)),
                ('right_column_lt', models.TextField(null=True, verbose_name='right column', blank=True)),
                ('right_column_pl', models.TextField(null=True, verbose_name='right column', blank=True)),
                ('right_column_ru', models.TextField(null=True, verbose_name='right column', blank=True)),
                ('right_column_uk', models.TextField(null=True, verbose_name='right column', blank=True)),
            ],
            options={
                'ordering': ('main_page', 'slug'),
                'verbose_name': 'info page',
                'verbose_name_plural': 'info pages',
            },
            bases=(models.Model,),
        ),
    ]
