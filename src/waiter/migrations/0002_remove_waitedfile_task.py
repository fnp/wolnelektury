# Generated by Django 2.2.16 on 2020-09-25 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waiter', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='waitedfile',
            name='task',
        ),
    ]
