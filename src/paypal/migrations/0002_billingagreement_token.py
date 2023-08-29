# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paypal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingagreement',
            name='token',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]
