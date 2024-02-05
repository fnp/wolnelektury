# Generated by Django 4.0.8 on 2023-05-29 09:06

import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0043_alter_bookmedia_duration_alter_bookmedia_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Snippet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sec', models.IntegerField()),
                ('text', models.TextField()),
                ('search_vector', django.contrib.postgres.search.SearchVectorField()),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.book')),
            ],
        ),
    ]