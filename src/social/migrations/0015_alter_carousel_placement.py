# Generated by Django 4.0.8 on 2022-10-28 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0014_auto_20221014_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carousel',
            name='placement',
            field=models.SlugField(choices=[('main', 'main'), ('main_2022', 'main 2022')], verbose_name='placement'),
        ),
    ]