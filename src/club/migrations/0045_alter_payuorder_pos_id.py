# Generated by Django 4.0.8 on 2024-01-31 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0044_alter_ambassador_options_alter_club_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payuorder',
            name='pos_id',
            field=models.CharField(blank=True, max_length=255, verbose_name='POS id'),
        ),
    ]
