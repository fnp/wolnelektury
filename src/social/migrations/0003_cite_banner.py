# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0002_auto_20151221_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='cite',
            name='banner',
            field=models.BooleanField(default=False, help_text='Adjust size to image, ignore the text', verbose_name='banner'),
        ),
    ]
