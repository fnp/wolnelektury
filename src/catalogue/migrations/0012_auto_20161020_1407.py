# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_auto_20160413_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookmedia',
            name='index',
            field=models.IntegerField(default=0, verbose_name='index'),
        ),
        migrations.AddField(
            model_name='bookmedia',
            name='part_name',
            field=models.CharField(default='', max_length=512, verbose_name='part name'),
        ),
    ]
