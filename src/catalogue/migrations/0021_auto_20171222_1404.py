# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import catalogue.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0020_book_cover_api_thumb'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='simple_cover',
            field=models.FileField(max_length=255, upload_to=catalogue.fields.UploadToPath('book/cover_simple/%s.jpg'), null=True, verbose_name='cover for mobile app', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='cover_api_thumb',
            field=models.FileField(max_length=255, upload_to=catalogue.fields.UploadToPath('book/cover_api_thumb/%s.jpg'), null=True, verbose_name='cover thumbnail for mobile app', blank=True),
        ),
    ]
