# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0006_legacy_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carouselitem',
            name='banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='social.Cite', verbose_name='banner'),
        ),
        migrations.AlterField(
            model_name='carouselitem',
            name='banner_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='social.BannerGroup', verbose_name='banner group'),
        ),
        migrations.AlterField(
            model_name='carouselitem',
            name='carousel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.Carousel', verbose_name='carousel'),
        ),
        migrations.AlterField(
            model_name='carouselitem',
            name='order',
            field=models.PositiveSmallIntegerField(unique=True, verbose_name='order'),
        ),
    ]
