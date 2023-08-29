# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
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
