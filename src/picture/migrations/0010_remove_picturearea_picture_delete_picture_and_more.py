# Generated by Django 4.0.8 on 2024-08-28 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0009_alter_picture_options_alter_picture_areas_json_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='picturearea',
            name='picture',
        ),
        migrations.DeleteModel(
            name='Picture',
        ),
        migrations.DeleteModel(
            name='PictureArea',
        ),
    ]
