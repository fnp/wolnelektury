# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0004_auto_20170725_1204'),
    ]

    operations = [
        migrations.CreateModel(
            name='BannerGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
            ],
            options={
                'verbose_name': 'banner group',
                'verbose_name_plural': 'banner groups',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Carousel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'carousel',
                'verbose_name_plural': 'carousels',
                'ordering': ('slug',),
            },
        ),
        migrations.CreateModel(
            name='CarouselItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(unique=True)),
            ],
            options={
                'verbose_name': 'carousel item',
                'verbose_name_plural': 'carousel items',
                'ordering': ('order',),
            },
        ),
        migrations.AddField(
            model_name='cite',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default='2007-09-17 12:00+00', verbose_name='created at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cite',
            name='picture',
            field=models.ImageField(blank=True, upload_to='', verbose_name='picture'),
        ),
        migrations.AddField(
            model_name='cite',
            name='video',
            field=models.URLField(blank=True, verbose_name='video'),
        ),
        migrations.AddField(
            model_name='carouselitem',
            name='banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='social.Cite'),
        ),
        migrations.AddField(
            model_name='carouselitem',
            name='banner_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='social.BannerGroup'),
        ),
        migrations.AddField(
            model_name='carouselitem',
            name='carousel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.Carousel'),
        ),
        migrations.AddField(
            model_name='cite',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='social.BannerGroup', verbose_name='group'),
        ),
        migrations.AlterUniqueTogether(
            name='carouselitem',
            unique_together=set([('carousel', 'order')]),
        ),
    ]
