# Generated by Django 2.2.25 on 2022-03-10 11:51

import catalogue.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0033_auto_20220128_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover_clean',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to=catalogue.fields.UploadToPath('book/cover_clean/%s.jpg'), verbose_name='clean cover'),
        ),
        migrations.AddField(
            model_name='book',
            name='cover_clean_etag',
            field=models.CharField(db_index=True, default='', editable=False, max_length=255),
        ),
    ]
