# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Consumer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('key', models.CharField(max_length=18)),
                ('secret', models.CharField(max_length=32)),
                ('status', models.CharField(default=b'pending', max_length=16, choices=[(b'pending', b'Pending approval'), (b'accepted', b'Accepted'), (b'canceled', b'Canceled')])),
                ('user', models.ForeignKey(related_name='consumers', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Nonce',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token_key', models.CharField(max_length=18)),
                ('consumer_key', models.CharField(max_length=18)),
                ('key', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('url', models.TextField(max_length=2047)),
                ('is_readonly', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=18)),
                ('secret', models.CharField(max_length=32)),
                ('token_type', models.IntegerField(choices=[(1, 'Request'), (2, 'Access')])),
                ('timestamp', models.IntegerField()),
                ('is_approved', models.BooleanField(default=False)),
                ('consumer', models.ForeignKey(to='piston.Consumer')),
                ('user', models.ForeignKey(related_name='tokens', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
