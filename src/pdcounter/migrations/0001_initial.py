# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='name', db_index=True)),
                ('slug', models.SlugField(unique=True, max_length=120, verbose_name='Slug')),
                ('sort_key', models.CharField(max_length=120, verbose_name='Sort key', db_index=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('death', models.IntegerField(null=True, verbose_name='Year of death', blank=True)),
                ('gazeta_link', models.CharField(max_length=240, blank=True)),
                ('wiki_link', models.CharField(max_length=240, blank=True)),
            ],
            options={
                'ordering': ('sort_key',),
                'verbose_name': 'author',
                'verbose_name_plural': 'authors',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookStub',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=120, verbose_name='Title')),
                ('author', models.CharField(max_length=120, verbose_name='author')),
                ('pd', models.IntegerField(null=True, verbose_name='Goes to public domain', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=120, verbose_name='Slug')),
                ('translator', models.TextField(verbose_name='Translator', blank=True)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Book stub',
                'verbose_name_plural': 'Book stubs',
            },
            bases=(models.Model,),
        ),
    ]
