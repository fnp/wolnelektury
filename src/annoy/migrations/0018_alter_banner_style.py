# Generated by Django 4.0.8 on 2024-12-06 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annoy', '0017_banner_progress_banner_target_alter_banner_place'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='style',
            field=models.CharField(blank=True, choices=[('blackout_full', 'Blackout — Cały ekran'), ('blackout_upper', 'Blackout — Górna połowa ekranu'), ('crisis_quiet', 'Kryzysowa — Spokojny'), ('crisis_loud', 'Kryzysowa — Ostry')], max_length=255, verbose_name='styl'),
        ),
    ]
