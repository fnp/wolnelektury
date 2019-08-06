# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0008_auto_20190403_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='cite',
            name='background_color',
            field=models.CharField(blank=True, max_length=32, verbose_name='background color'),
        ),
        migrations.AddField(
            model_name='cite',
            name='picture_alt',
            field=models.CharField(blank=True, max_length=255, verbose_name='picture alternative text'),
        ),
        migrations.AddField(
            model_name='cite',
            name='picture_author',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='picture author'),
        ),
        migrations.AddField(
            model_name='cite',
            name='picture_license',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='picture license name'),
        ),
        migrations.AddField(
            model_name='cite',
            name='picture_license_link',
            field=models.URLField(blank=True, null=True, verbose_name='picture license link'),
        ),
        migrations.AddField(
            model_name='cite',
            name='picture_link',
            field=models.URLField(blank=True, null=True, verbose_name='picture link'),
        ),
        migrations.AddField(
            model_name='cite',
            name='picture_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='picture title'),
        ),
    ]
