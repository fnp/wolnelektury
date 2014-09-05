# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deleted',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField()),
                ('slug', models.SlugField(max_length=120, verbose_name='Slug', blank=True)),
                ('category', models.CharField(db_index=True, max_length=64, null=True, blank=True)),
                ('created_at', models.DateTimeField(editable=False, db_index=True)),
                ('deleted_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='deleted',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
