# Generated by Django 4.0.8 on 2022-10-28 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0039_collection_authors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
            preserve_default=False,
        ),
    ]
