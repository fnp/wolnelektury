# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libraries', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='slug',
            field=models.SlugField(unique=True, max_length=120, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='library',
            name='description',
            field=models.TextField(verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='library',
            name='slug',
            field=models.SlugField(max_length=120, unique=True, null=True, verbose_name='slug'),
        ),
    ]
