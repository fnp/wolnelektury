# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0008_membership_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='default_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='default amount'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='plan',
            name='min_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='min amount'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='method',
            field=models.CharField(choices=[('payu', 'PayU'), ('payu-re', 'PayU Recurring'), ('paypal', 'PayPal')], max_length=255, verbose_name='method'),
        ),
    ]
