# Generated by Django 2.2.25 on 2022-03-10 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0034_auto_20220310_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookmedia',
            name='duration',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
