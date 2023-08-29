# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120, verbose_name='name')),
                ('_description', models.CharField(max_length=255, verbose_name='Description', blank=True)),
                ('logo', models.ImageField(upload_to='sponsorzy/sponsor/logo', verbose_name='logo')),
                ('url', models.URLField(verbose_name='url', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SponsorPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120, verbose_name='name')),
                ('sponsors', models.TextField(default='{}', verbose_name='sponsors')),
                ('_html', models.TextField(editable=False, blank=True)),
                ('sprite', models.ImageField(upload_to='sponsorzy/sprite', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
