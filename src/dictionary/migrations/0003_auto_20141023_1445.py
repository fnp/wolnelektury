# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_auto_20141006_1422'),
    ]

    operations = [
        migrations.CreateModel(
            name='Qualifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qualifier', models.CharField(unique=True, max_length=128, db_index=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['qualifier'],
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='note',
            name='qualifier',
        ),
        migrations.AddField(
            model_name='note',
            name='qualifiers',
            field=models.ManyToManyField(to='dictionary.Qualifier', null=True),
            preserve_default=True,
        ),
    ]
