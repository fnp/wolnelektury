# Generated by Django 2.2.27 on 2022-08-26 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0041_move_amounts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='club',
            name='monthly_amounts',
        ),
        migrations.RemoveField(
            model_name='club',
            name='single_amounts',
        ),
    ]