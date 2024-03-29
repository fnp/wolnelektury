# Generated by Django 2.2.19 on 2021-06-14 08:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0032_collection_listed'),
        ('stats', '0004_auto_20210601_1303'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayVisits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('views', models.IntegerField()),
                ('unique_views', models.IntegerField()),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.Book')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
