# Generated by Django 2.2.6 on 2019-12-11 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annoy', '0003_auto_20191211_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='action_label',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='banner',
            name='close_label',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
