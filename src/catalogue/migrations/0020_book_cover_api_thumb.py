# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import catalogue.fields
import catalogue.models.book


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0019_auto_20171221_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover_api_thumb',
            field=catalogue.fields.EbookField(b'cover_api_thumb', max_length=255, upload_to=catalogue.models.book.UploadToPath(b'book/cover_api_thumb/%s.jpg'), null=True, verbose_name='cover thumbnail for API', blank=True),
        ),
    ]
