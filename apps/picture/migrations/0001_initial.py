# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields
import jsonfield.fields
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=120, verbose_name='Title')),
                ('slug', models.SlugField(unique=True, max_length=120, verbose_name='Slug')),
                ('sort_key', models.CharField(verbose_name='Sort key', max_length=120, editable=False, db_index=True)),
                ('sort_key_author', models.CharField(default='', verbose_name='sort key by author', max_length=120, editable=False, db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='creation date', db_index=True)),
                ('changed_at', models.DateTimeField(auto_now=True, verbose_name='creation date', db_index=True)),
                ('xml_file', models.FileField(upload_to=b'xml', storage=django.core.files.storage.FileSystemStorage(base_url=b'/media/pictures/', location=b'/home/rczajka/workspace/wolnelektury/media/pictures'), verbose_name=b'xml_file')),
                ('image_file', sorl.thumbnail.fields.ImageField(upload_to=b'images', storage=django.core.files.storage.FileSystemStorage(base_url=b'/media/pictures/', location=b'/home/rczajka/workspace/wolnelektury/media/pictures'), verbose_name='image_file')),
                ('html_file', models.FileField(upload_to=b'html', storage=django.core.files.storage.FileSystemStorage(base_url=b'/media/pictures/', location=b'/home/rczajka/workspace/wolnelektury/media/pictures'), verbose_name=b'html_file')),
                ('areas_json', jsonfield.fields.JSONField(default={}, verbose_name='picture areas JSON', editable=False)),
                ('extra_info', jsonfield.fields.JSONField(default={}, verbose_name='Additional information')),
                ('culturepl_link', models.CharField(max_length=240, blank=True)),
                ('wiki_link', models.CharField(max_length=240, blank=True)),
                ('_related_info', jsonfield.fields.JSONField(null=True, editable=False, blank=True)),
                ('width', models.IntegerField(null=True)),
                ('height', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ('sort_key',),
                'verbose_name': 'picture',
                'verbose_name_plural': 'pictures',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PictureArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('area', jsonfield.fields.JSONField(default={}, verbose_name='area', editable=False)),
                ('kind', models.CharField(db_index=True, max_length=10, verbose_name='form', choices=[(b'thing', 'thing'), (b'theme', 'motif')])),
                ('picture', models.ForeignKey(related_name=b'areas', to='picture.Picture')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
