# Generated by Django 2.2.19 on 2021-06-10 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annoy', '0010_auto_20210430_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='background_color',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='banner',
            name='text_color',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
