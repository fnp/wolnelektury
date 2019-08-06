# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0009_auto_20190510_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='email_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='method',
            field=models.CharField(choices=[('payu', 'PayU'), ('payu-re', 'PayU (płatność odnawialna)')], max_length=255, verbose_name='method'),
        ),
    ]
