# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0021_auto_20171222_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookpopularity',
            name='count',
            field=models.IntegerField(default=0, db_index=True),
        ),
    ]
