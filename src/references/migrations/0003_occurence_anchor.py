# Generated by Django 4.0.8 on 2024-09-18 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0002_remove_reference_first_section_occurence'),
    ]

    operations = [
        migrations.AddField(
            model_name='occurence',
            name='anchor',
            field=models.CharField(default='', max_length=64),
            preserve_default=False,
        ),
    ]
