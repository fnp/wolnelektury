# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0003_auto_20140924_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='title',
            field=models.CharField(max_length=32767, verbose_name='Title'),
        ),
    ]
