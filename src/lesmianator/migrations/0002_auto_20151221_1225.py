# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesmianator', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poem',
            name='created_from',
            field=models.TextField(null=True, verbose_name='extra information', blank=True),
        ),
        migrations.AlterField(
            model_name='poem',
            name='slug',
            field=models.SlugField(max_length=120, verbose_name='slug'),
        ),
    ]
