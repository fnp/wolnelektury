# Generated by Django 3.2.16 on 2022-10-14 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0013_auto_20210120_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carouselitem',
            name='order',
            field=models.PositiveSmallIntegerField(verbose_name='order'),
        ),
        migrations.AlterUniqueTogether(
            name='carouselitem',
            unique_together=set(),
        ),
    ]