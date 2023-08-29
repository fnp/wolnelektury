# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0003_cite_banner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cite',
            name='text',
            field=models.TextField(verbose_name='text', blank=True),
        ),
    ]
