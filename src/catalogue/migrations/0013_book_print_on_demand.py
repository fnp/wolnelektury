# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_auto_20161020_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='print_on_demand',
            field=models.BooleanField(default=False, verbose_name='print on demand'),
        ),
    ]
