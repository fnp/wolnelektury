# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
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
            field=catalogue.fields.EbookField('simple_cover', max_length=255, upload_to=catalogue.fields.UploadToPath('book/cover_simple/%s.jpg'), null=True, verbose_name='cover for mobile app', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='cover_api_thumb',
            field=catalogue.fields.EbookField('cover_api_thumb', max_length=255, upload_to=catalogue.fields.UploadToPath('book/cover_api_thumb/%s.jpg'), null=True, verbose_name='cover thumbnail for mobile app', blank=True),
        ),
    ]
