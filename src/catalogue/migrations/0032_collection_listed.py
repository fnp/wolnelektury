# Generated by Django 2.2.19 on 2021-05-05 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0031_auto_20210316_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='listed',
            field=models.BooleanField(db_index=True, default=True, verbose_name='listed'),
        ),
    ]