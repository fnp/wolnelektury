# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isbn', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='onixrecord',
            options={'ordering': ['isbn_pool__id', 'suffix']},
        ),
    ]
