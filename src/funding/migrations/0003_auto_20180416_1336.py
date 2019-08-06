# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funding', '0002_auto_20151221_1225'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='funding',
            options={'ordering': ['-payed_at', 'pk'], 'verbose_name': 'funding', 'verbose_name_plural': 'fundings'},
        ),
    ]
