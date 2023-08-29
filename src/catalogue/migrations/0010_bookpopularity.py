# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_auto_20160127_1019'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookPopularity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(default=0)),
                ('book', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='popularity', to='catalogue.Book')),
            ],
        ),
    ]
