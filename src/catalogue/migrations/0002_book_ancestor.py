# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='ancestor',
            field=models.ManyToManyField(related_name='descendant', null=True, editable=False, to='catalogue.Book', blank=True),
            preserve_default=True,
        ),
    ]
