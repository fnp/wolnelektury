# Generated by Django 2.2.16 on 2020-11-26 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0005_auto_20200129_1309'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'verbose_name': 'contact', 'verbose_name_plural': 'contacts'},
        ),
        migrations.AlterField(
            model_name='contact',
            name='level',
            field=models.PositiveSmallIntegerField(choices=[(10, 'Cold'), (20, 'Would-be donor'), (30, 'One-time donor'), (40, 'Recurring donor'), (45, 'Manually set as member'), (50, 'Opt out')]),
        ),
    ]
