# Generated by Django 2.2.19 on 2021-05-19 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0025_auto_20201126_1250'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='source',
            field=models.CharField(blank=True, max_length=255, verbose_name='source'),
        ),
    ]
