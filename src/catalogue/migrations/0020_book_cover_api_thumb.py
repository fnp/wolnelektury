# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import catalogue.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0019_auto_20171221_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover_api_thumb',
            field=models.FileField(max_length=255, upload_to=catalogue.fields.UploadToPath('book/cover_api_thumb/%s.jpg'), null=True, verbose_name='cover thumbnail for API', blank=True),
        ),
    ]
