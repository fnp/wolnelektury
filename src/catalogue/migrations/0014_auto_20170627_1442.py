# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import fnpdjango.storage
import catalogue.models.bookmedia


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0013_book_print_on_demand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmedia',
            name='file',
            field=models.FileField(storage=fnpdjango.storage.BofhFileSystemStorage(), upload_to=catalogue.models.bookmedia._file_upload_to, max_length=600, verbose_name='file'),
        ),
    ]
