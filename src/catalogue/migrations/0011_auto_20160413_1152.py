# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_bookpopularity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ('sort_key_author', 'sort_key'), 'verbose_name': 'book', 'verbose_name_plural': 'books'},
        ),
    ]
