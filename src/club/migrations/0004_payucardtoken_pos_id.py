# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0003_remove_payuorder_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='payucardtoken',
            name='pos_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
