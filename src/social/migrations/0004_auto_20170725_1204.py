# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
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
