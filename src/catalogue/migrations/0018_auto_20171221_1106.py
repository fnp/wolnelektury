# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0017_auto_20171214_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmedia',
            name='part_name',
            field=models.CharField(default='', max_length=512, verbose_name='part name', blank=True),
        ),
    ]
