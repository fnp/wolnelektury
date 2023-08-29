# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0006_auto_20190416_1236'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='payunotification',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_set', to='club.PayUOrder'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='method',
            field=models.CharField(choices=[('payu', 'PayU'), ('payu-re', 'PayU Recurring'), ('paypal-re', 'PayPal Recurring')], max_length=255, verbose_name='method'),
        ),
    ]
