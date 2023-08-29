# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('funding', '0003_auto_20180416_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funding',
            name='offer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='funding.Offer', verbose_name='offer'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='book',
            field=models.ForeignKey(blank=True, help_text='Published book.', null=True, on_delete=django.db.models.deletion.PROTECT, to='catalogue.Book'),
        ),
        migrations.AlterField(
            model_name='spent',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalogue.Book'),
        ),
    ]
