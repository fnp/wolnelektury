# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isbn', '0003_isbnpool_purpose'),
    ]

    operations = [
        migrations.AddField(
            model_name='onixrecord',
            name='dc_slug',
            field=models.CharField(default='', max_length=256, db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='onixrecord',
            unique_together=set([('isbn_pool', 'suffix')]),
        ),
    ]
