# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0014_auto_20170627_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='recommended',
            field=models.BooleanField(default=False, verbose_name='recommended'),
        ),
    ]
