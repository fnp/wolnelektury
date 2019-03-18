# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import join
import sorl.thumbnail.fields
from django.conf import settings
from django.db import migrations, models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0006_auto_20151221_1225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='html_file',
            field=models.FileField(upload_to='html', storage=django.core.files.storage.FileSystemStorage(base_url='/media/pictures/', location=join(settings.MEDIA_ROOT, 'pictures')), verbose_name='html file'),
        ),
        migrations.AlterField(
            model_name='picture',
            name='image_file',
            field=sorl.thumbnail.fields.ImageField(upload_to='images', storage=django.core.files.storage.FileSystemStorage(base_url='/media/pictures/', location=join(settings.MEDIA_ROOT, 'pictures')), verbose_name='image file'),
        ),
        migrations.AlterField(
            model_name='picture',
            name='xml_file',
            field=models.FileField(upload_to='xml', storage=django.core.files.storage.FileSystemStorage(base_url='/media/pictures/', location=join(settings.MEDIA_ROOT, 'pictures')), verbose_name='xml file'),
        ),
    ]
