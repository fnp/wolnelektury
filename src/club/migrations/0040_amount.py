# Generated by Django 2.2.27 on 2022-08-26 12:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0039_auto_20220421_0109'),
    ]

    operations = [
        migrations.CreateModel(
            name='SingleAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('description', models.TextField(blank=True)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.Club')),
            ],
            options={
                'ordering': ['amount'],
            },
        ),
        migrations.CreateModel(
            name='MonthlyAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('description', models.TextField(blank=True)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.Club')),
            ],
            options={
                'ordering': ['amount'],
            },
        ),
    ]