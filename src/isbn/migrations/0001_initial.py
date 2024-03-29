# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ISBNPool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prefix', models.CharField(max_length=10)),
                ('suffix_from', models.IntegerField()),
                ('suffix_to', models.IntegerField()),
                ('ref_from', models.IntegerField()),
                ('next_suffix', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ONIXRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datestamp', models.DateField(auto_now=True)),
                ('suffix', models.IntegerField()),
                ('product_form', models.CharField(max_length=4)),
                ('product_form_detail', models.CharField(max_length=8, blank=True)),
                ('title', models.CharField(max_length=256)),
                ('part_number', models.CharField(max_length=64, blank=True)),
                ('contributors', models.TextField()),
                ('edition_type', models.CharField(max_length=4)),
                ('edition_number', models.IntegerField(default=1)),
                ('language', models.CharField(max_length=4)),
                ('imprint', models.CharField(max_length=256)),
                ('publishing_date', models.DateField()),
                ('isbn_pool', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='isbn.ISBNPool')),
            ],
        ),
    ]
