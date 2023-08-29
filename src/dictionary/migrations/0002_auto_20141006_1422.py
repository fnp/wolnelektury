# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0004_remove_booktags_count_related_info'),
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoteSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anchor', models.CharField(max_length=64)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.Book')),
                ('note', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.Note')),
            ],
            options={
                'ordering': ['book'],
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='note',
            name='anchor',
        ),
        migrations.RemoveField(
            model_name='note',
            name='book',
        ),
        migrations.AddField(
            model_name='note',
            name='fn_type',
            field=models.CharField(default='', max_length=10, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='note',
            name='language',
            field=models.CharField(default='', max_length=10, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='note',
            name='qualifier',
            field=models.CharField(default='', max_length=128, db_index=True, blank=True),
            preserve_default=False,
        ),
    ]
