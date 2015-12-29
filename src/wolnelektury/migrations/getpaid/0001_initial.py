# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import getpaid.abstract_mixin


class Migration(migrations.Migration):

    dependencies = [
        ('funding', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(verbose_name='amount', max_digits=20, decimal_places=4)),
                ('currency', models.CharField(max_length=3, verbose_name='currency')),
                ('status', models.CharField(default=b'new', max_length=20, verbose_name='status', db_index=True, choices=[(b'new', 'new'), (b'in_progress', 'in progress'), (b'partially_paid', 'partially paid'), (b'paid', 'paid'), (b'failed', 'failed')])),
                ('backend', models.CharField(max_length=50, verbose_name='backend')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on', db_index=True)),
                ('paid_on', models.DateTimeField(default=None, null=True, verbose_name='paid on', db_index=True, blank=True)),
                ('amount_paid', models.DecimalField(default=0, verbose_name='amount paid', max_digits=20, decimal_places=4)),
                ('external_id', models.CharField(max_length=64, null=True, verbose_name='external id', blank=True)),
                ('description', models.CharField(max_length=128, null=True, verbose_name='Description', blank=True)),
                ('order', models.ForeignKey(related_name=b'payment', to='funding.Funding')),
            ],
            options={
                'ordering': ('-created_on',),
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
            },
            bases=(models.Model, getpaid.abstract_mixin.AbstractMixin),
        ),
    ]
