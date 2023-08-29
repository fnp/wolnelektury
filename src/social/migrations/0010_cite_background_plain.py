# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0009_auto_20190715_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='cite',
            name='background_plain',
            field=models.BooleanField(default=False, verbose_name='plain background'),
        ),
    ]
