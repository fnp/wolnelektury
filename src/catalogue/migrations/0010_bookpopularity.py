# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_auto_20160127_1019'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookPopularity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(default=0)),
                ('book', models.OneToOneField(related_name='popularity', to='catalogue.Book')),
            ],
        ),
    ]
