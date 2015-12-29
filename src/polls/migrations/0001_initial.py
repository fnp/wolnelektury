# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.TextField(verbose_name='question')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('open', models.BooleanField(default=False, verbose_name='open')),
            ],
            options={
                'verbose_name': 'Poll',
                'verbose_name_plural': 'Polls',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PollItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(verbose_name='content')),
                ('vote_count', models.IntegerField(default=0, verbose_name='vote count')),
                ('poll', models.ForeignKey(related_name=b'items', to='polls.Poll')),
            ],
            options={
                'verbose_name': 'vote item',
                'verbose_name_plural': 'vote items',
            },
            bases=(models.Model,),
        ),
    ]
