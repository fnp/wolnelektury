# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('push', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-timestamp']},
        ),
        migrations.RemoveField(
            model_name='notification',
            name='image_url',
        ),
        migrations.AddField(
            model_name='notification',
            name='image',
            field=models.FileField(upload_to='push/img', verbose_name='image', blank=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='body',
            field=models.CharField(max_length=2048, verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='title',
            field=models.CharField(max_length=256, verbose_name='title'),
        ),
    ]
