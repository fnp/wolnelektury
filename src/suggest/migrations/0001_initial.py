# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PublishingSuggestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact', models.CharField(max_length=120, verbose_name='Contact', blank=True)),
                ('books', models.TextField(null=True, verbose_name='Books', blank=True)),
                ('audiobooks', models.TextField(null=True, verbose_name='audiobooks', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('ip', models.GenericIPAddressField(verbose_name='IP address')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
                'verbose_name': 'publishing suggestion',
                'verbose_name_plural': 'publishing suggestions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact', models.CharField(max_length=120, verbose_name='Contact', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='creation date')),
                ('ip', models.GenericIPAddressField(verbose_name='IP address')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
                'verbose_name': 'suggestion',
                'verbose_name_plural': 'suggestions',
            },
            bases=(models.Model,),
        ),
    ]
