# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_bookuserdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookuserdata',
            name='last_changed',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 28, 14, 41, 2, 673054, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
