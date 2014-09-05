# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Funding',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=127, verbose_name='name', blank=True)),
                ('email', models.EmailField(db_index=True, max_length=75, verbose_name='email', blank=True)),
                ('amount', models.DecimalField(verbose_name='amount', max_digits=10, decimal_places=2)),
                ('payed_at', models.DateTimeField(db_index=True, null=True, verbose_name='payed at', blank=True)),
                ('language_code', models.CharField(max_length=2, null=True, blank=True)),
                ('notifications', models.BooleanField(default=True, db_index=True, verbose_name='notifications')),
                ('notify_key', models.CharField(max_length=32)),
            ],
            options={
                'ordering': ['-payed_at'],
                'verbose_name': 'funding',
                'verbose_name_plural': 'fundings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author', models.CharField(max_length=255, verbose_name='author')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('target', models.DecimalField(verbose_name='target', max_digits=10, decimal_places=2)),
                ('start', models.DateField(verbose_name='start', db_index=True)),
                ('end', models.DateField(verbose_name='end', db_index=True)),
                ('redakcja_url', models.URLField(verbose_name='redakcja URL', blank=True)),
                ('cover', models.ImageField(upload_to=b'funding/covers', verbose_name='Cover')),
                ('notified_near', models.DateTimeField(null=True, verbose_name='Near-end notifications sent', blank=True)),
                ('notified_end', models.DateTimeField(null=True, verbose_name='End notifications sent', blank=True)),
                ('book', models.ForeignKey(blank=True, to='catalogue.Book', help_text='Published book.', null=True)),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='polls.Poll', help_text='Poll', null=True)),
            ],
            options={
                'ordering': ['-end'],
                'verbose_name': 'offer',
                'verbose_name_plural': 'offers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Perk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(verbose_name='price', max_digits=10, decimal_places=2)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('long_name', models.CharField(max_length=255, verbose_name='long name')),
                ('end_date', models.DateField(null=True, verbose_name='end date', blank=True)),
                ('offer', models.ForeignKey(verbose_name='offer', blank=True, to='funding.Offer', null=True)),
            ],
            options={
                'ordering': ['-price'],
                'verbose_name': 'perk',
                'verbose_name_plural': 'perks',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Spent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(verbose_name='amount', max_digits=10, decimal_places=2)),
                ('timestamp', models.DateField(verbose_name='when')),
                ('book', models.ForeignKey(to='catalogue.Book')),
            ],
            options={
                'ordering': ['-timestamp'],
                'verbose_name': 'money spent on a book',
                'verbose_name_plural': 'money spent on books',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='funding',
            name='offer',
            field=models.ForeignKey(verbose_name='offer', to='funding.Offer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='funding',
            name='perks',
            field=models.ManyToManyField(to='funding.Perk', verbose_name='perks', blank=True),
            preserve_default=True,
        ),
    ]
