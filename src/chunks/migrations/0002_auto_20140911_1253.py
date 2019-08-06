# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models, migrations


def null_to_blank(apps, schema_editor):
    Chunk = apps.get_model("chunks", "Chunk")
    Chunk.objects.filter(content=None).update(content='')
    Chunk.objects.filter(description=None).update(description='')


class Migration(migrations.Migration):

    dependencies = [
        ('chunks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(null_to_blank),
        migrations.AlterField(
            model_name='chunk',
            name='content',
            field=models.TextField(verbose_name='content', blank=True),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='description',
            field=models.CharField(max_length=255, verbose_name='Description', blank=True),
        ),
    ]
