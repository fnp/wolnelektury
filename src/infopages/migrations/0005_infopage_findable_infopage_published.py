# Generated by Django 4.0.8 on 2024-03-12 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infopages', '0004_alter_infopage_options_alter_infopage_left_column_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='infopage',
            name='findable',
            field=models.BooleanField(default=True, verbose_name='wyszukiwalna'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='infopage',
            name='published',
            field=models.BooleanField(default=True, help_text='Nieopublikowane strony są widoczne tylko dla administratorów.', verbose_name='opublikowana'),
            preserve_default=False,
        ),
    ]
