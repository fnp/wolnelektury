# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_auto_20141023_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='qualifiers',
            field=models.ManyToManyField(to='dictionary.Qualifier'),
        ),
    ]
