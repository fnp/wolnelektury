# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import catalogue.fields
import catalogue.models.bookmedia


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0013_book_print_on_demand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmedia',
            name='file',
            field=models.FileField(storage=catalogue.fields.OverwriteStorage(), upload_to=catalogue.models.bookmedia._file_upload_to, max_length=600, verbose_name='file'),
        ),
    ]
