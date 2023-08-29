# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0025_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='preview_key',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
