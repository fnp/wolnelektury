# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anchor', models.CharField(max_length=64)),
                ('html', models.TextField()),
                ('sort_key', models.CharField(max_length=128, db_index=True)),
                ('book', models.ForeignKey(to='catalogue.Book')),
            ],
            options={
                'ordering': ['sort_key'],
            },
            bases=(models.Model,),
        ),
    ]
