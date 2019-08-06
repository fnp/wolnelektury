# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getpaid', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='description',
            field=models.CharField(max_length=128, null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(default='new', max_length=20, verbose_name='status', db_index=True, choices=[('new', 'new'), ('in_progress', 'in progress'), ('accepted_for_proc', 'accepted for processing'), ('partially_paid', 'partially paid'), ('paid', 'paid'), ('cancelled', 'cancelled'), ('failed', 'failed')]),
        ),
    ]
