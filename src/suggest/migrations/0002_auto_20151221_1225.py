# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suggest', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publishingsuggestion',
            name='books',
            field=models.TextField(null=True, verbose_name='books', blank=True),
        ),
        migrations.AlterField(
            model_name='publishingsuggestion',
            name='contact',
            field=models.CharField(max_length=120, verbose_name='contact', blank=True),
        ),
        migrations.AlterField(
            model_name='suggestion',
            name='contact',
            field=models.CharField(max_length=120, verbose_name='contact', blank=True),
        ),
        migrations.AlterField(
            model_name='suggestion',
            name='description',
            field=models.TextField(verbose_name='description', blank=True),
        ),
    ]
