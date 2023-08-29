# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0007_auto_20190318_1339'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cite',
            options={'ordering': ('vip', 'text'), 'verbose_name': 'banner', 'verbose_name_plural': 'banners'},
        ),
    ]
