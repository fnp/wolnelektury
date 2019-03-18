# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=64)),
                ('file', models.FileField(upload_to='contact/attachment')),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='submission date')),
                ('ip', models.GenericIPAddressField(verbose_name='IP address')),
                ('contact', models.EmailField(max_length=128, verbose_name='contact')),
                ('form_tag', models.CharField(max_length=32, verbose_name='form', db_index=True)),
                ('body', jsonfield.fields.JSONField(verbose_name='body')),
            ],
            options={
                'ordering': ('-created_at',),
                'verbose_name': 'submitted form',
                'verbose_name_plural': 'submitted forms',
            },
        ),
        migrations.AddField(
            model_name='attachment',
            name='contact',
            field=models.ForeignKey(to='contact.Contact'),
        ),
    ]
