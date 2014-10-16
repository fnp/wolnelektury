# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0004_remove_booktags_count_related_info'),
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoteSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anchor', models.CharField(max_length=64)),
                ('book', models.ForeignKey(to='catalogue.Book')),
                ('note', models.ForeignKey(to='dictionary.Note')),
            ],
            options={
                'ordering': ['book'],
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='note',
            name='anchor',
        ),
        migrations.RemoveField(
            model_name='note',
            name='book',
        ),
        migrations.AddField(
            model_name='note',
            name='fn_type',
            field=models.CharField(default='', max_length=10, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='note',
            name='language',
            field=models.CharField(default='', max_length=10, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='note',
            name='qualifier',
            field=models.CharField(default='', max_length=128, db_index=True, blank=True),
            preserve_default=False,
        ),
    ]
