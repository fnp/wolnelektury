# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('isbn', '0004_auto_20180215_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onixrecord',
            name='isbn_pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='isbn.ISBNPool'),
        ),
    ]
