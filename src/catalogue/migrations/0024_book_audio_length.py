# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0023_book_abstract'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='audio_length',
            field=models.CharField(max_length=8, verbose_name='audio length', blank=True),
        ),
    ]
