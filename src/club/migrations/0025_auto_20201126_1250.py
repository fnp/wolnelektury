# Generated by Django 2.2.16 on 2020-11-26 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0024_auto_20201126_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='manual',
            field=models.BooleanField(default=False, verbose_name='manual'),
        ),
    ]
