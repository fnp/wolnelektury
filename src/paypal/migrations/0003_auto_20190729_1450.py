# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('paypal', '0002_billingagreement_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingagreement',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='paypal.BillingPlan'),
        ),
        migrations.AlterField(
            model_name='billingagreement',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
