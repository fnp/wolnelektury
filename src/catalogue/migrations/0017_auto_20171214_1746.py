# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0016_auto_20171031_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='changed_at',
            field=models.DateTimeField(auto_now=True, verbose_name='change date', db_index=True),
        ),
    ]
