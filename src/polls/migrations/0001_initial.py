# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import models, migrations
import django.db.models.deletion


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
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='polls.Poll')),
            ],
            options={
                'verbose_name': 'vote item',
                'verbose_name_plural': 'vote items',
            },
            bases=(models.Model,),
        ),
    ]
