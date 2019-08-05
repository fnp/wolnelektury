# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import catalogue.fields
import catalogue.models.bookmedia


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_auto_20151123_1529'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ('sort_key',), 'verbose_name': 'book', 'verbose_name_plural': 'books'},
        ),
        migrations.AlterModelOptions(
            name='fragment',
            options={'ordering': ('book', 'anchor'), 'verbose_name': 'fragment', 'verbose_name_plural': 'fragments'},
        ),
        migrations.AlterField(
            model_name='book',
            name='ancestor',
            field=models.ManyToManyField(related_name='descendant', editable=False, to='catalogue.Book', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='common_slug',
            field=models.SlugField(max_length=120, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='book',
            name='description',
            field=models.TextField(verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='extra_info',
            field=models.TextField(default='{}', verbose_name='extra information'),
        ),
        migrations.AlterField(
            model_name='book',
            name='parent_number',
            field=models.IntegerField(default=0, verbose_name='parent number'),
        ),
        migrations.AlterField(
            model_name='book',
            name='slug',
            field=models.SlugField(unique=True, max_length=120, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='book',
            name='sort_key',
            field=models.CharField(verbose_name='sort key', max_length=120, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=32767, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='bookmedia',
            name='extra_info',
            field=models.TextField(default='{}', verbose_name='extra information', editable=False),
        ),
        migrations.AlterField(
            model_name='bookmedia',
            name='file',
            field=catalogue.fields.OverwritingFileField(upload_to=catalogue.models.bookmedia._file_upload_to, max_length=600, verbose_name='file'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='book_slugs',
            field=models.TextField(verbose_name='book slugs'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='description',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='description_de',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='description_en',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='description_es',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='description_fr',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='description_it',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='description_lt',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='description_pl',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='description_ru',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='description_uk',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='kind',
            field=models.CharField(default='book', max_length=10, verbose_name='kind', db_index=True, choices=[('book', 'book'), ('picture', 'picture')]),
        ),
        migrations.AlterField(
            model_name='collection',
            name='slug',
            field=models.SlugField(max_length=120, serialize=False, verbose_name='slug', primary_key=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title',
            field=models.CharField(max_length=120, verbose_name='title', db_index=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title_de',
            field=models.CharField(max_length=120, null=True, verbose_name='title', db_index=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title_en',
            field=models.CharField(max_length=120, null=True, verbose_name='title', db_index=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title_es',
            field=models.CharField(max_length=120, null=True, verbose_name='title', db_index=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title_fr',
            field=models.CharField(max_length=120, null=True, verbose_name='title', db_index=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title_it',
            field=models.CharField(max_length=120, null=True, verbose_name='title', db_index=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title_lt',
            field=models.CharField(max_length=120, null=True, verbose_name='title', db_index=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title_pl',
            field=models.CharField(max_length=120, null=True, verbose_name='title', db_index=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title_ru',
            field=models.CharField(max_length=120, null=True, verbose_name='title', db_index=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title_uk',
            field=models.CharField(max_length=120, null=True, verbose_name='title', db_index=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='category',
            field=models.CharField(db_index=True, max_length=50, verbose_name='category', choices=[('author', 'author'), ('epoch', 'epoch'), ('kind', 'kind'), ('genre', 'genre'), ('theme', 'theme'), ('set', 'set'), ('thing', 'thing')]),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description',
            field=models.TextField(verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description_de',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description_en',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description_es',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description_fr',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description_it',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description_lt',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description_pl',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description_ru',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description_uk',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=120, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='sort_key',
            field=models.CharField(max_length=120, verbose_name='sort key', db_index=True),
        ),
    ]
