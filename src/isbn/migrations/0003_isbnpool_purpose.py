# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isbn', '0002_auto_20180213_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='isbnpool',
            name='purpose',
            field=models.CharField(default='', max_length=4, choices=[('WL', 'Wolne Lektury'), ('FNP', 'Fundacja Nowoczesna Polska')]),
            preserve_default=False,
        ),
    ]
