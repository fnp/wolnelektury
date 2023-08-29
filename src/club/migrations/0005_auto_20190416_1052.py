# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0004_payucardtoken_pos_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payucardtoken',
            name='disposable_token',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='payucardtoken',
            name='reusable_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='payucardtoken',
            unique_together=set([('pos_id', 'reusable_token'), ('pos_id', 'disposable_token')]),
        ),
    ]
