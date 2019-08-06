# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('key', models.CharField(help_text='A unique name for this attachment', max_length=255, serialize=False, verbose_name='key', primary_key=True)),
                ('attachment', models.FileField(upload_to='chunks/attachment')),
            ],
            options={
                'ordering': ('key',),
                'verbose_name': 'attachment',
                'verbose_name_plural': 'attachments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Chunk',
            fields=[
                ('key', models.CharField(help_text='A unique name for this piece of content', max_length=255, serialize=False, verbose_name='key', primary_key=True)),
                ('description', models.CharField(max_length=255, null=True, verbose_name='Description', blank=True)),
                ('content', models.TextField(null=True, verbose_name='content', blank=True)),
                ('content_de', models.TextField(null=True, verbose_name='content', blank=True)),
                ('content_en', models.TextField(null=True, verbose_name='content', blank=True)),
                ('content_es', models.TextField(null=True, verbose_name='content', blank=True)),
                ('content_fr', models.TextField(null=True, verbose_name='content', blank=True)),
                ('content_it', models.TextField(null=True, verbose_name='content', blank=True)),
                ('content_lt', models.TextField(null=True, verbose_name='content', blank=True)),
                ('content_pl', models.TextField(null=True, verbose_name='content', blank=True)),
                ('content_ru', models.TextField(null=True, verbose_name='content', blank=True)),
                ('content_uk', models.TextField(null=True, verbose_name='content', blank=True)),
            ],
            options={
                'ordering': ('key',),
                'verbose_name': 'piece',
                'verbose_name_plural': 'pieces',
            },
            bases=(models.Model,),
        ),
    ]
