# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120, verbose_name='name')),
                ('slug', models.SlugField(unique=True, max_length=120, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'catalog',
                'verbose_name_plural': 'catalogs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120, verbose_name='name', blank=True)),
                ('slug', models.SlugField(max_length=120, unique=True, null=True, verbose_name='Slug')),
                ('url', models.CharField(max_length=120, verbose_name='url', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('catalog', models.ForeignKey(related_name='libraries', on_delete=django.db.models.deletion.PROTECT, to='libraries.Catalog')),
            ],
            options={
                'verbose_name': 'library',
                'verbose_name_plural': 'libraries',
            },
            bases=(models.Model,),
        ),
    ]
