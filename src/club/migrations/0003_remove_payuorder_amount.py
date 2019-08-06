# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0002_auto_20190416_1024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payuorder',
            name='amount',
        ),
    ]
