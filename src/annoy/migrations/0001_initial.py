# Generated by Django 2.2.6 on 2019-12-11 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.SlugField(choices=[('top', 'Top of all pages.'), ('book-page', 'Book page'), ('book-text-intermission', 'Book text intermission'), ('fragment-list', 'Next to list of book fragments.')])),
                ('text', models.TextField()),
                ('text_de', models.TextField(null=True)),
                ('text_en', models.TextField(null=True)),
                ('text_es', models.TextField(null=True)),
                ('text_fr', models.TextField(null=True)),
                ('text_it', models.TextField(null=True)),
                ('text_lt', models.TextField(null=True)),
                ('text_pl', models.TextField(null=True)),
                ('text_ru', models.TextField(null=True)),
                ('text_uk', models.TextField(null=True)),
                ('url', models.CharField(max_length=1024)),
                ('priority', models.PositiveSmallIntegerField(default=0)),
                ('since', models.DateTimeField(blank=True, null=True)),
                ('until', models.DateTimeField(blank=True, null=True)),
                ('show_members', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'banner',
                'verbose_name_plural': 'banners',
                'ordering': ('place', '-priority'),
            },
        ),
        migrations.CreateModel(
            name='DynamicTextInsert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paragraphs', models.IntegerField(verbose_name='pararaphs')),
                ('text', models.TextField(verbose_name='text')),
                ('text_de', models.TextField(null=True, verbose_name='text')),
                ('text_en', models.TextField(null=True, verbose_name='text')),
                ('text_es', models.TextField(null=True, verbose_name='text')),
                ('text_fr', models.TextField(null=True, verbose_name='text')),
                ('text_it', models.TextField(null=True, verbose_name='text')),
                ('text_lt', models.TextField(null=True, verbose_name='text')),
                ('text_pl', models.TextField(null=True, verbose_name='text')),
                ('text_ru', models.TextField(null=True, verbose_name='text')),
                ('text_uk', models.TextField(null=True, verbose_name='text')),
                ('url', models.CharField(max_length=1024)),
            ],
            options={
                'verbose_name': 'dynamic insert',
                'verbose_name_plural': 'dynamic inserts',
                'ordering': ('paragraphs',),
            },
        ),
    ]
