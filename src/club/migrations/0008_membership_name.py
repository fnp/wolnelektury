# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0007_auto_20190416_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
