# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fnpdjango.storage
import jsonfield.fields
import catalogue.fields
import catalogue.models.bookmedia
from django.conf import settings
import catalogue.models.book


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=120, verbose_name='Title')),
                ('sort_key', models.CharField(verbose_name='Sort key', max_length=120, editable=False, db_index=True)),
                ('sort_key_author', models.CharField(default='', verbose_name='sort key by author', max_length=120, editable=False, db_index=True)),
                ('slug', models.SlugField(unique=True, max_length=120, verbose_name='Slug')),
                ('common_slug', models.SlugField(max_length=120, verbose_name='Slug')),
                ('language', models.CharField(default=b'pol', max_length=3, verbose_name='language code', db_index=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='creation date', db_index=True)),
                ('changed_at', models.DateTimeField(auto_now=True, verbose_name='creation date', db_index=True)),
                ('parent_number', models.IntegerField(default=0, verbose_name='Parent number')),
                ('extra_info', jsonfield.fields.JSONField(default={}, verbose_name='Additional information')),
                ('gazeta_link', models.CharField(max_length=240, blank=True)),
                ('wiki_link', models.CharField(max_length=240, blank=True)),
                ('cover', catalogue.fields.EbookField(b'cover', upload_to=catalogue.models.book._cover_upload_to, storage=fnpdjango.storage.BofhFileSystemStorage(), max_length=255, blank=True, null=True, verbose_name='cover')),
                ('cover_thumb', catalogue.fields.EbookField(b'cover_thumb', max_length=255, upload_to=catalogue.models.book._cover_thumb_upload_to, null=True, verbose_name='cover thumbnail', blank=True)),
                ('_related_info', jsonfield.fields.JSONField(null=True, editable=False, blank=True)),
                ('txt_file', catalogue.fields.EbookField(b'txt', default=b'', storage=fnpdjango.storage.BofhFileSystemStorage(), upload_to=catalogue.models.book._txt_upload_to, max_length=255, blank=True, verbose_name='TXT file')),
                ('fb2_file', catalogue.fields.EbookField(b'fb2', default=b'', storage=fnpdjango.storage.BofhFileSystemStorage(), upload_to=catalogue.models.book._fb2_upload_to, max_length=255, blank=True, verbose_name='FB2 file')),
                ('pdf_file', catalogue.fields.EbookField(b'pdf', default=b'', storage=fnpdjango.storage.BofhFileSystemStorage(), upload_to=catalogue.models.book._pdf_upload_to, max_length=255, blank=True, verbose_name='PDF file')),
                ('epub_file', catalogue.fields.EbookField(b'epub', default=b'', storage=fnpdjango.storage.BofhFileSystemStorage(), upload_to=catalogue.models.book._epub_upload_to, max_length=255, blank=True, verbose_name='EPUB file')),
                ('mobi_file', catalogue.fields.EbookField(b'mobi', default=b'', storage=fnpdjango.storage.BofhFileSystemStorage(), upload_to=catalogue.models.book._mobi_upload_to, max_length=255, blank=True, verbose_name='MOBI file')),
                ('html_file', catalogue.fields.EbookField(b'html', default=b'', storage=fnpdjango.storage.BofhFileSystemStorage(), upload_to=catalogue.models.book._html_upload_to, max_length=255, blank=True, verbose_name='HTML file')),
                ('xml_file', catalogue.fields.EbookField(b'xml', default=b'', storage=fnpdjango.storage.BofhFileSystemStorage(), upload_to=catalogue.models.book._xml_upload_to, max_length=255, blank=True, verbose_name='XML file')),
                ('parent', models.ForeignKey(related_name=b'children', blank=True, to='catalogue.Book', null=True)),
            ],
            options={
                'ordering': ('sort_key',),
                'verbose_name': 'book',
                'verbose_name_plural': 'Books',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookMedia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(db_index=True, max_length=20, verbose_name='type', choices=[(b'mp3', 'MP3 file'), (b'ogg', 'Ogg Vorbis file'), (b'daisy', 'DAISY file')])),
                ('name', models.CharField(max_length=512, verbose_name='name')),
                ('file', catalogue.fields.OverwritingFileField(upload_to=catalogue.models.bookmedia._file_upload_to, max_length=600, verbose_name='XML file')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='creation date', db_index=True)),
                ('extra_info', jsonfield.fields.JSONField(default={}, verbose_name='Additional information', editable=False)),
                ('source_sha1', models.CharField(max_length=40, null=True, editable=False, blank=True)),
                ('book', models.ForeignKey(related_name=b'media', to='catalogue.Book')),
            ],
            options={
                'ordering': ('type', 'name'),
                'verbose_name': 'book media',
                'verbose_name_plural': 'book media',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('title', models.CharField(max_length=120, verbose_name='Title', db_index=True)),
                ('title_de', models.CharField(max_length=120, null=True, verbose_name='Title', db_index=True)),
                ('title_en', models.CharField(max_length=120, null=True, verbose_name='Title', db_index=True)),
                ('title_es', models.CharField(max_length=120, null=True, verbose_name='Title', db_index=True)),
                ('title_fr', models.CharField(max_length=120, null=True, verbose_name='Title', db_index=True)),
                ('title_it', models.CharField(max_length=120, null=True, verbose_name='Title', db_index=True)),
                ('title_lt', models.CharField(max_length=120, null=True, verbose_name='Title', db_index=True)),
                ('title_pl', models.CharField(max_length=120, null=True, verbose_name='Title', db_index=True)),
                ('title_ru', models.CharField(max_length=120, null=True, verbose_name='Title', db_index=True)),
                ('title_uk', models.CharField(max_length=120, null=True, verbose_name='Title', db_index=True)),
                ('slug', models.SlugField(max_length=120, serialize=False, verbose_name='Slug', primary_key=True)),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_de', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_en', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_es', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_fr', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_it', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_lt', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_pl', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_ru', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_uk', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('book_slugs', models.TextField(verbose_name='Book stubs')),
                ('kind', models.CharField(default=b'book', max_length=10, verbose_name='form', db_index=True, choices=[(b'book', 'book'), (b'picture', b'picture')])),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'collection',
                'verbose_name_plural': 'collections',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Fragment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('short_text', models.TextField(editable=False)),
                ('anchor', models.CharField(max_length=120)),
                ('book', models.ForeignKey(related_name=b'fragments', to='catalogue.Book')),
            ],
            options={
                'ordering': ('book', 'anchor'),
                'verbose_name': 'Fragment',
                'verbose_name_plural': 'Fragments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('netloc', models.CharField(max_length=120, serialize=False, verbose_name='network location', primary_key=True)),
                ('name', models.CharField(max_length=120, verbose_name='name', blank=True)),
                ('name_de', models.CharField(max_length=120, null=True, verbose_name='name', blank=True)),
                ('name_en', models.CharField(max_length=120, null=True, verbose_name='name', blank=True)),
                ('name_es', models.CharField(max_length=120, null=True, verbose_name='name', blank=True)),
                ('name_fr', models.CharField(max_length=120, null=True, verbose_name='name', blank=True)),
                ('name_it', models.CharField(max_length=120, null=True, verbose_name='name', blank=True)),
                ('name_lt', models.CharField(max_length=120, null=True, verbose_name='name', blank=True)),
                ('name_pl', models.CharField(max_length=120, null=True, verbose_name='name', blank=True)),
                ('name_ru', models.CharField(max_length=120, null=True, verbose_name='name', blank=True)),
                ('name_uk', models.CharField(max_length=120, null=True, verbose_name='name', blank=True)),
            ],
            options={
                'ordering': ('netloc',),
                'verbose_name': 'source',
                'verbose_name_plural': 'sources',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='name', db_index=True)),
                ('name_de', models.CharField(max_length=50, null=True, verbose_name='name', db_index=True)),
                ('name_en', models.CharField(max_length=50, null=True, verbose_name='name', db_index=True)),
                ('name_es', models.CharField(max_length=50, null=True, verbose_name='name', db_index=True)),
                ('name_fr', models.CharField(max_length=50, null=True, verbose_name='name', db_index=True)),
                ('name_it', models.CharField(max_length=50, null=True, verbose_name='name', db_index=True)),
                ('name_lt', models.CharField(max_length=50, null=True, verbose_name='name', db_index=True)),
                ('name_pl', models.CharField(max_length=50, null=True, verbose_name='name', db_index=True)),
                ('name_ru', models.CharField(max_length=50, null=True, verbose_name='name', db_index=True)),
                ('name_uk', models.CharField(max_length=50, null=True, verbose_name='name', db_index=True)),
                ('slug', models.SlugField(max_length=120, verbose_name='Slug')),
                ('sort_key', models.CharField(max_length=120, verbose_name='Sort key', db_index=True)),
                ('category', models.CharField(db_index=True, max_length=50, verbose_name='Category', choices=[(b'author', 'author'), (b'epoch', 'period'), (b'kind', 'form'), (b'genre', 'genre'), (b'theme', 'motif'), (b'set', 'set'), (b'book', 'book'), (b'thing', 'thing')])),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('description_de', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_en', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_es', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_fr', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_it', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_lt', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_pl', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_ru', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_uk', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('book_count', models.IntegerField(null=True, verbose_name='Number of books', blank=True)),
                ('picture_count', models.IntegerField(null=True, verbose_name='picture count', blank=True)),
                ('gazeta_link', models.CharField(max_length=240, blank=True)),
                ('culturepl_link', models.CharField(max_length=240, blank=True)),
                ('wiki_link', models.CharField(max_length=240, blank=True)),
                ('wiki_link_de', models.CharField(max_length=240, null=True, blank=True)),
                ('wiki_link_en', models.CharField(max_length=240, null=True, blank=True)),
                ('wiki_link_es', models.CharField(max_length=240, null=True, blank=True)),
                ('wiki_link_fr', models.CharField(max_length=240, null=True, blank=True)),
                ('wiki_link_it', models.CharField(max_length=240, null=True, blank=True)),
                ('wiki_link_lt', models.CharField(max_length=240, null=True, blank=True)),
                ('wiki_link_pl', models.CharField(max_length=240, null=True, blank=True)),
                ('wiki_link_ru', models.CharField(max_length=240, null=True, blank=True)),
                ('wiki_link_uk', models.CharField(max_length=240, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='creation date', db_index=True)),
                ('changed_at', models.DateTimeField(auto_now=True, verbose_name='creation date', db_index=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('sort_key',),
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(verbose_name='object id', db_index=True)),
                ('content_type', models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType')),
                ('tag', models.ForeignKey(related_name=b'items', verbose_name='tag', to='catalogue.Tag')),
            ],
            options={
                'db_table': 'catalogue_tag_relation',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='tagrelation',
            unique_together=set([('tag', 'content_type', 'object_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('slug', 'category')]),
        ),
    ]
