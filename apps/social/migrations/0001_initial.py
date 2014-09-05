# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='text')),
                ('small', models.BooleanField(default=False, help_text='Make this cite display smaller.', verbose_name='small')),
                ('vip', models.CharField(max_length=128, null=True, verbose_name='VIP', blank=True)),
                ('link', models.URLField(verbose_name='link')),
                ('sticky', models.BooleanField(default=False, help_text='Sticky cites will take precedense.', db_index=True, verbose_name='sticky')),
                ('image', models.ImageField(help_text='Best image is exactly 975px wide and weights under 100kB.', upload_to=b'social/cite', null=True, verbose_name='image', blank=True)),
                ('image_shift', models.IntegerField(help_text='Vertical shift, in percents. 0 means top, 100 is bottom. Default is 50%.', null=True, verbose_name='shift', blank=True)),
                ('image_title', models.CharField(max_length=255, null=True, verbose_name='Title', blank=True)),
                ('image_author', models.CharField(max_length=255, null=True, verbose_name='author', blank=True)),
                ('image_link', models.URLField(null=True, verbose_name='link', blank=True)),
                ('image_license', models.CharField(max_length=255, null=True, verbose_name='license name', blank=True)),
                ('image_license_link', models.URLField(null=True, verbose_name='license link', blank=True)),
                ('book', models.ForeignKey(verbose_name='book', blank=True, to='catalogue.Book', null=True)),
            ],
            options={
                'ordering': ('vip', 'text'),
                'verbose_name': 'cite',
                'verbose_name_plural': 'cites',
            },
            bases=(models.Model,),
        ),
    ]
