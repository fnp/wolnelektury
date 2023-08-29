# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0005_auto_20190416_1052'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='payucardtoken',
            unique_together=set([]),
        ),
    ]
