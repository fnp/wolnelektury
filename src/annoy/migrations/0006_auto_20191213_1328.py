# Generated by Django 2.2.6 on 2019-12-13 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annoy', '0005_auto_20191211_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='staff_preview',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='banner',
            name='action_label',
            field=models.CharField(blank=True, help_text='', max_length=255),
        ),
    ]